import os
import uuid

import pymupdf
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from backend.ai_assistant import generate_answer
from backend.document_search import search_document
from backend.pdf_reader import read_pdf

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(os.path.join(app.root_path, "temp"), exist_ok=True)

document_context = {"filename": None, "pages": []}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "Please select a PDF file."}), 400

    uploaded_file = request.files["pdf"]
    if not uploaded_file.filename:
        return jsonify({"error": "Please select a PDF file."}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(uploaded_file.filename)}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    uploaded_file.save(file_path)

    try:
        pages, total_pages = read_pdf(file_path)
        if total_pages == 0:
            raise ValueError("The PDF does not contain readable pages.")

        document_context["filename"] = secure_filename(uploaded_file.filename)
        document_context["pages"] = pages
        document_context["file_path"] = file_path
        return jsonify({
            "success": True,
            "filename": document_context["filename"],
            "total_pages": total_pages,
            "message": "PDF uploaded and processed successfully.",
        })
    except (pymupdf.FileDataError, ValueError, RuntimeError) as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        document_context.update({"filename": None, "pages": [], "file_path": None})
        return jsonify({"error": str(exc)}), 400
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        document_context.update({"filename": None, "pages": [], "file_path": None})
        return jsonify({"error": "Unable to read this PDF file."}), 400


@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not document_context["filename"]:
        return jsonify({"error": "Please upload a PDF first."}), 400
    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    passages = search_document(document_context["pages"], question)
    if not passages:
        return jsonify({
            "answer": "I could not find relevant information in the uploaded document.",
            "sources": [],
        })

    try:
        answer = generate_answer(question, passages)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify({
        "answer": answer,
        "sources": [passage["page"] for passage in passages],
    })


@app.route("/remove-document", methods=["POST"])
def remove_document():
    file_path = document_context.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    document_context.update({"filename": None, "pages": [], "file_path": None})
    return jsonify({"success": True, "message": "Document removed."})


@app.errorhandler(413)
def upload_too_large(_error):
    return jsonify({"error": "The PDF must be 10 MB or smaller."}), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
