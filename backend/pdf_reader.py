import pymupdf


def read_pdf(file_path):
    """Extract text from every page while preserving the original page number."""
    pages = []

    try:
        with pymupdf.open(file_path) as document:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()
                if text:
                    pages.append({"page": page_number, "text": text})

            total_pages = document.page_count
    except (pymupdf.FileDataError, RuntimeError) as exc:
        raise RuntimeError("The PDF is unreadable or is not a valid PDF.") from exc

    if total_pages == 0:
        raise ValueError("The PDF does not contain readable pages.")
    if not pages:
        raise ValueError("No readable text was found. Scanned PDFs are not supported yet.")

    return pages, total_pages
