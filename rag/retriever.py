_store: list = []

def store_result(results):
    global _store
    _store = results["results"]

def retrieve_context(query: str) -> str:
    if not _store:
        return ""
    # Just join all content into one context string
    return "\n\n".join(r["content"] for r in _store)