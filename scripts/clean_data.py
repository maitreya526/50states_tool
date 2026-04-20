import pandas as pd
import json
import unicodedata

INPUT_PATH = "data/raw/all_laws.csv"
OUTPUT_PATH = "data/processed/state_laws.json"


# -----------------------------
# CLEAN TEXT (fix encoding issues)
# -----------------------------
def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # normalize unicode (fix broken encodings)
    text = unicodedata.normalize("NFKD", text)

    # fix common bad sequences
    replacements = {
        "\u00e2\u20ac\u00a2": "•",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"'
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # remove non-ascii (optional but safe here)
    text = text.encode("ascii", "ignore").decode("ascii")

    return text.strip()


# -----------------------------
# CLEAN INT
# -----------------------------
def clean_int(value):
    if pd.isna(value):
        return None

    try:
        return int(value)
    except:
        return None


# -----------------------------
# TIMELINE
# -----------------------------
def clean_timeline(value):
    if pd.isna(value):
        return {"type": "flexible", "days": None}

    text = str(value).strip().lower()

    if "not specified" in text or text == "":
        return {"type": "flexible", "days": None}

    try:
        return {"type": "fixed", "days": int(text)}
    except:
        return {"type": "flexible", "days": None}


# -----------------------------
# MAIN
# -----------------------------
def main():
    # try utf-8 first, fallback if needed
    try:
        df = pd.read_csv(INPUT_PATH, encoding="utf-8")
    except:
        df = pd.read_csv(INPUT_PATH, encoding="latin1")

    # normalize column names
    df.columns = df.columns.str.strip()

    print("COLUMNS:", df.columns.tolist())

    state_laws = {}

    for _, row in df.iterrows():
        state = str(row["State"]).strip().lower().replace(" ", "_")

        ag_type = str(row["AG_type"]).strip().lower()

        state_laws[state] = {
            "timeline": clean_timeline(row["timeline_days(individual)"]),
            "ag": {
                "type": ag_type if ag_type in ["none", "conditional", "mandatory"] else "none",
                "threshold": clean_int(row["AG_threshold"]),
                "deadline_days": clean_int(row["AG_days"])
            },
            "meta": {
                "pii_definition": clean_text(row["Definition_of _PII"]),
                "ag_text": clean_text(row["Notification to AG"]),
                "penalty_text": clean_text(row["Penalty"])
            }
        }

        # debug one state
        if state == "alabama":
            print("DEBUG ALABAMA:", state_laws[state])

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(state_laws, f, indent=2, ensure_ascii=False)

    print(f"Saved cleaned JSON to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()