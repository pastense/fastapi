import regex as re

def clean_content(raw_text: str) -> str:
    cleaned = raw_text.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)  # collapse whitespace
    cleaned = re.sub(r'(Accept all cookies|Sign up for newsletter).*', '', cleaned, flags=re.IGNORECASE)
    return cleaned[:5000]  # clip to OpenAI limit

