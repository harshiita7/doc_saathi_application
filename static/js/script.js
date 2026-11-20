/**
 * GovGuide AI — script.js
 * Clean & minimal interactions for file upload and document Q&A.
 */

const pdfInput       = document.getElementById("pdf-input");
const uploadButton   = document.getElementById("upload-button");
const removeButton   = document.getElementById("remove-button");
const documentName   = document.getElementById("document-name");
const documentStatus = document.getElementById("document-status");
const documentPages  = document.getElementById("document-pages");
const questionForm   = document.getElementById("question-form");
const questionInput  = document.getElementById("question-input");
const sendButton     = document.getElementById("send-button");
const chatMessages   = document.getElementById("chat-messages");
const emptyState     = document.getElementById("empty-state");
let uploadedDocument = null;

/**
 * Append a chat message bubble
 */
function addMessage(text, role, sources = []) {
  if (emptyState && emptyState.parentNode) {
    emptyState.remove();
  }

  const message = document.createElement("div");
  message.className = `chat-msg ${role}`;
  message.textContent = text;

  if (sources.length) {
    const uniquePages = [...new Set(sources)].sort((a, b) => a - b);
    const sourceEl = document.createElement("div");
    sourceEl.className = "source-tag";
    sourceEl.textContent = `Source: ${uniquePages.map(p => `Page ${p}`).join(", ")}`;
    message.appendChild(sourceEl);
  }

  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return message;
}

/**
 * Display uploaded document info
 */
function setDocumentState(name, pages) {
  documentName.textContent = name;
  documentStatus.textContent = "Ready for questions";
  documentStatus.className = "doc-status status-ready";
  documentPages.textContent = `${pages} page${pages !== 1 ? "s" : ""} indexed`;
  removeButton.hidden = false;
}

/**
 * Reset sidebar state
 */
function clearDocumentState() {
  documentName.textContent = "No document uploaded";
  documentStatus.textContent = "Waiting for file";
  documentStatus.className = "doc-status status-waiting";
  documentPages.textContent = "";
  removeButton.hidden = true;
  pdfInput.value = "";
  uploadedDocument = null;
}

// Open file selector
uploadButton?.addEventListener("click", () => pdfInput.click());

// Handle PDF upload
pdfInput?.addEventListener("change", async () => {
  if (!pdfInput.files.length) return;

  const originalContent = uploadButton.innerHTML;
  uploadButton.disabled = true;
  uploadButton.style.opacity = "0.7";
  uploadButton.innerHTML = `<div class="upload-text">Processing Document...</div>`;

  const formData = new FormData();
  formData.append("pdf", pdfInput.files[0]);

  try {
    const response = await fetch("/upload", { method: "POST", body: formData });
    const rawText = await response.text();
    let data;
    try {
      data = JSON.parse(rawText);
    } catch {
      throw new Error(
        `Upload service returned an invalid response (${response.status}). Please try again.`
      );
    }

    if (!response.ok) throw new Error(data.error || "Upload failed.");

    setDocumentState(data.filename, data.total_pages);
    uploadedDocument = {
      filename: data.filename,
      pages: data.pages,
    };
    addMessage(
      `"${data.filename}" is loaded (${data.total_pages} pages). You can now ask any question regarding this document.`,
      "assistant"
    );
  } catch (error) {
    alert(error.message);
  } finally {
    uploadButton.disabled = false;
    uploadButton.style.opacity = "1";
    uploadButton.innerHTML = originalContent;
  }
});

// Remove document
removeButton?.addEventListener("click", async () => {
  try {
    const response = await fetch("/remove-document", { method: "POST" });
    const rawText = await response.text();
    let data;
    try {
      data = JSON.parse(rawText);
    } catch {
      throw new Error(
        `Server returned an invalid response (${response.status}). Please try again.`
      );
    }
    if (!response.ok) throw new Error(data.error || "Could not remove the document.");
    clearDocumentState();
  } catch (error) {
    alert(error.message);
  }
});

// Ask question
questionForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  addMessage(question, "user");
  questionInput.value = "";
  sendButton.disabled = true;

  const loadingBubble = addMessage("Searching document & formulating answer...", "loading");

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        filename: uploadedDocument?.filename,
        pages: uploadedDocument?.pages,
      }),
    });

    const rawText = await response.text();
    let data;
    try {
      data = JSON.parse(rawText);
    } catch {
      throw new Error(
        `Server returned an invalid response (${response.status}). Please try again.`
      );
    }
    loadingBubble.remove();

    if (!response.ok) throw new Error(data.error || "Could not generate an answer.");

    addMessage(data.answer, "assistant", data.sources || []);
  } catch (error) {
    loadingBubble.remove();
    addMessage(`Error: ${error.message}`, "assistant");
  } finally {
    sendButton.disabled = false;
    questionInput.focus();
  }
});
