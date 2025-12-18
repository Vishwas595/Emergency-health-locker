import re


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_name_case(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split())


def extract_name(text: str) -> str:
    lines = text.splitlines()

    for line in lines:
        raw = normalize_spaces(line)

        match = re.match(
            r"^(Mr|Mrs|Ms)\s*(?:\.\s*)?\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)$",
            raw,
            re.IGNORECASE
        )

        if match:
            title = match.group(1).capitalize()
            name_part = clean_name_case(match.group(2))
            return f"{title} {name_part}"

    return ""


def extract_hba1c(text: str) -> str:
    lines = text.splitlines()

    for i, line in enumerate(lines):
        if "hb a1c" in line.lower():
            for j in range(i + 1, min(i + 4, len(lines))):
                value_match = re.search(r"\b(\d+\.\d+)\s*%", lines[j])
                if value_match:
                    return value_match.group(1) + " %"

    return ""


def extract_fasting_sugar(text: str) -> str:
    match = re.search(
        r"BLOOD\s+SUGAR\s*\(\s*FASTING\s*\)\s*([0-9.]+)",
        text,
        re.IGNORECASE
    )
    if match:
        return match.group(1) + " mg/dl"
    return ""


def map_medical_data(text: str) -> dict:
    data = {}

    name = extract_name(text)
    if name:
        data["Name"] = name

    hba1c = extract_hba1c(text)
    if hba1c:
        data["HbA1c"] = hba1c

    sugar = extract_fasting_sugar(text)
    if sugar:
        data["Fasting_Sugar"] = sugar

    bg_match = re.search(r"\b(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)\b", text)
    if bg_match:
        data["Blood_Group"] = bg_match.group(1)

    return data
