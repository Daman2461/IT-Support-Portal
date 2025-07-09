import re

def redact_pii(text: str) -> str:
    # Redact emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', text)
    # Redact names (simple heuristic: capitalized words, not at sentence start)
    text = re.sub(r'(?<!\.)\s([A-Z][a-z]+\s[A-Z][a-z]+)', ' [REDACTED_NAME]', text)
    return text
