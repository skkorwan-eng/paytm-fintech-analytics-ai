import re
from disclosure_snippets import DISCLOSURE_SNIPPETS

def extract_signals(snippet: str) -> dict:
    text = snippet.lower()
    flags = []
    if "litigation" in text:
        flags.append("litigation")
    if "regulatory" in text or "regulator" in text or "data-localization" in text:
        flags.append("regulatory")
    if "top three customers" in text or "customer concentration" in text or "42 percent of total revenue" in text:
        flags.append("customer concentration")

    hedging = any(p in text for p in ["assuming", "cautiously", "visibility"])
    if "confident" in text or "approved" in text:
        sentiment = "confident"
    elif hedging:
        sentiment = "cautious"
    else:
        sentiment = "neutral"

    return {
        "risk_flags": flags,
        "hedging_detected": hedging,
        "sentiment": sentiment,
    }

if __name__ == "__main__":
    print("DISCLOSURE EXTRACTION | MOCK_LLM baseline")
    for snippet in DISCLOSURE_SNIPPETS:
        doc = snippet.split(":", 1)[0]
        print(doc, extract_signals(snippet))
