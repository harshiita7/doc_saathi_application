# GovGuide AI — NESFIC-D-36

An AI-powered Government Document Assistant that lets users upload official PDF documents and ask plain-language questions, receiving grounded answers with supporting page references.

---

## Features

| Feature | Description |
|---|---|
| **PDF Upload** | Upload any government PDF (up to 10 MB) |
| **Smart PDF Reading** | Extracts text page-by-page using PyMuPDF |
| **Document Search** | Keyword-based search finds the most relevant passages |
| **AI Answers** | Gemini AI generates clear, plain-English answers |
| **Source References** | Every answer cites the exact PDF page numbers |
| **Responsive UI** | Works on desktop and mobile |

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python + Flask |
| PDF Reading | PyMuPDF |
| AI Integration | Google Gemini API (`google-genai`) |
| Environment | python-dotenv |

---

## Project Structure

```
GovGuide-AI/
├── app.py                  # Main Flask application (routes)
├── config.py               # App configuration
├── requirements.txt        # Python dependencies
├── .env                    # API key (never commit this)
├── .env.example            # Template for .env
├── .gitignore
├── README.md
│
├── backend/
│   ├── __init__.py
│   ├── pdf_reader.py       # Extracts text from PDF pages
│   ├── document_search.py  # Keyword search over extracted pages
│   └── ai_assistant.py     # Sends context + question to Gemini
│
├── templates/
│   ├── index.html          # Homepage
│   └── chat.html           # AI Assistant interface
│
├── static/
│   ├── css/style.css       # All styling (homepage + chat)
│   ├── js/script.js        # Upload, chat, and fetch logic
│   └── images/             # (Place logo.png here)
│
├── uploads/                # Uploaded PDFs (auto-cleaned)
└── temp/                   # Temporary files
```

---

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/harshiita7/doc_saathi_application)

After starting the deployment, set `GEMINI_API_KEY` in the Render service environment variables.

---

## Setup Instructions

### 1. Clone / open in VS Code

```bash
# Already inside GovGuide-AI folder
```

### 2. Create and activate the virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com) and generate an API key.
2. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

> ⚠️ Never commit `.env` to GitHub. It is already in `.gitignore`.

### 5. Run the application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## How to Use

1. Click **Get Started** on the homepage.
2. Click **Upload PDF** and select a government document.
3. Wait for the confirmation message — the document is now ready.
4. Type your question in the input box and press **Send**.
5. Read the AI-generated answer and the **source page numbers** shown below it.
6. Click **Remove document** to upload a different PDF.

---

## Testing Checklist

| Test | Expected Result |
|---|---|
| Upload a valid PDF | Filename + page count appear in the sidebar |
| Upload a non-PDF file | Error: "Only PDF files are supported." |
| Upload a PDF > 10 MB | Error: "The PDF must be 10 MB or smaller." |
| Ask about content in the document | Accurate answer with page references |
| Ask about something not in the document | "Could not find the answer in the uploaded document." |
| Ask a question before uploading | Error: "Please upload a PDF first." |
| Ask with the input box empty | Form does not submit |

---

## Development Milestones

| Milestone | Status |
|---|---|
| M1 – Project structure + design | ✅ Complete |
| M2 – PDF upload + reading | ✅ Complete |
| M3 – Document search | ✅ Complete |
| M4 – Gemini AI integration | ✅ Complete |
| M5 – Full working prototype | ✅ Complete |

---

## Disclaimer

GovGuide AI is intended for informational and educational purposes. Always verify important decisions against the original government document.
