import re

def extract_bold_text(text: str) -> list[str]:
    # Naive LLM approach: just use regex, completely missing the escaped stars logic \*\*
    # and probably grabbing single stars * as part of the content incorrectly or failing to match correctly.
    # LLMs love to write simplistic regex for these parsing problems.
    pattern = r'\*\*(.*?)\*\*'
    return re.findall(pattern, text)
