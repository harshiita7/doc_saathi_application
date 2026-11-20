import re


def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def search_document(pages, question, limit=4):
    """Find relevant passages with a beginner-friendly keyword overlap score."""
    question_words = _words(question)
    stop_words = {
        "the", "a", "an", "is", "are", "of", "to", "for", "in", "on",
        "what", "who", "how", "when", "where", "which", "please",
    }
    question_words -= stop_words
    synonyms = {
        "documents": {"certificate", "certificates", "proof", "proofs", "document", "documents", "submit"},
        "document": {"certificate", "certificates", "proof", "proofs", "document", "documents", "submit"},
        "required": {"required", "must", "submit", "necessary", "need", "needful"},
        "requirements": {"required", "must", "submit", "necessary", "need", "eligibility", "eligible"},
        "eligibility": {"eligible", "eligibility", "qualify", "qualification", "criteria"},
        "eligible": {"eligible", "eligibility", "qualify", "qualification", "criteria"},
        "purpose": {"purpose", "objective", "aim", "goal", "scheme"},
        "procedure": {"procedure", "process", "steps", "apply", "application", "submit"},
        "application": {"application", "apply", "procedure", "process", "submit"},
    }
    expanded_words = set(question_words)
    for word in question_words:
        expanded_words.update(synonyms.get(word, set()))
    question_words = expanded_words
    if not question_words:
        return []

    results = []
    for page in pages:
        page_words = _words(page["text"])
        overlap = len(question_words & page_words)
        if overlap:
            results.append({
                "page": page["page"],
                "text": page["text"],
                "_score": overlap,
            })

    results.sort(key=lambda result: result["_score"], reverse=True)
    relevant = results[:limit]
    for result in relevant:
        result.pop("_score", None)
    return relevant
