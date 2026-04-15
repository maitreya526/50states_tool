import pandas as pd
import json
import re

INPUT_PATH = "data/raw/all_laws.csv"
OUTPUT_PATH = "data/processed/state_laws.json"


# -----------------------------
# TEXT NORMALIZATION
# -----------------------------
def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)

    # fix numbers like 1,000 → 1000
    text = re.sub(r"(\d),(\d)", r"\1\2", text)

    return text.lower()


# -----------------------------
# PII BUCKET
# -----------------------------
def pii_bucket(x):
    try:
        x = int(x)
    except:
        return "unknown"

    if x <= 3:
        return "narrow"
    elif x <= 7:
        return "medium"
    else:
        return "broad"


# -----------------------------
# TIMELINE
# -----------------------------
def parse_timeline(val):
    if pd.isna(val):
        return {"type": "flexible", "days": None}

    try:
        return {"type": "fixed", "days": int(val)}
    except:
        return {"type": "flexible", "days": None}


# -----------------------------
# THRESHOLD
# -----------------------------
def extract_threshold(text):
    text = normalize_text(text)

    # conditional patterns
    match = re.search(
        r"(more than|over|greater than|exceeding|at least|if)\s+\D*?(\d{2,6})\s*(residents|individuals|persons|consumers)",
        text
    )
    if match:
        return int(match.group(2))

    # fallback
    match2 = re.search(
        r"(\d{2,6})\s*(residents|individuals|persons|consumers)",
        text
    )
    if match2:
        return int(match2.group(1))

    return None


# -----------------------------
# DEADLINE
# -----------------------------
def extract_deadline(text):
    text = normalize_text(text)

    # days
    match_days = re.search(r"(within|no later than)\s+(\d+)\s*day", text)
    if match_days:
        return int(match_days.group(2)), "days"

    # hours
    match_hours = re.search(r"(within|no later than)\s+(\d+)\s*hour", text)
    if match_hours:
        return int(match_hours.group(2)), "hours"

    return None, None


# -----------------------------
# AG PARSER (CORE + META)
# -----------------------------
def parse_ag(text):
    raw = normalize_text(text)

    if raw == "":
        return {
            "type": "none",
            "threshold": None,
            "deadline_days": None,
            "deadline_hours": None,
            "meta": {},
            "raw_text": ""
        }

    threshold = extract_threshold(raw)
    deadline_value, unit = extract_deadline(raw)

    deadline_days = None
    deadline_hours = None

    if unit == "days":
        deadline_days = deadline_value
    elif unit == "hours":
        deadline_hours = deadline_value

    # determine type (fixed bug: no "no" substring issue)
    if re.search(r"\bno\s+notification\b|\bnot\s+required\b", raw):
        ag_type = "none"
    elif threshold is not None:
        ag_type = "conditional"
    elif re.search(r"\bmust notify\b|\bshall notify\b", raw):
        ag_type = "mandatory"
    else:
        ag_type = "unknown"

    # CLEAN invalid threshold
    if threshold is not None and threshold < 50:
        threshold = None

    # META extraction (very light, no overengineering)
    conditions = []
    if "after determination" in raw:
        conditions.append("after_determination")
    if "same time" in raw:
        conditions.append("simultaneous_with_consumer")

    return {
        "type": ag_type,
        "threshold": threshold,
        "deadline_days": deadline_days,
        "deadline_hours": deadline_hours,
        "meta": {
            "conditions": conditions
        },
        "raw_text": raw
    }


# -----------------------------
# PENALTY
# -----------------------------
def parse_penalty(text):
    raw = normalize_text(text)

    if raw == "":
        return {
            "type": "unknown",
            "raw_text": ""
        }

    if "per" in raw and "record" in raw:
        p_type = "per_record"
    elif "cap" in raw or "max" in raw:
        p_type = "capped"
    elif "unfair" in raw:
        p_type = "unfair_practice"
    else:
        p_type = "unknown"

    return {
        "type": p_type,
        "raw_text": raw
    }


# -----------------------------
# MAIN
# -----------------------------
def main():
    df = pd.read_csv(INPUT_PATH)

    state_laws = {}

    for _, row in df.iterrows():
        state = str(row["State"]).strip().lower().replace(" ", "_")

        state_laws[state] = {
            "pii_bucket": pii_bucket(row["PII(types)"]),
            "timeline": parse_timeline(row["timeline_days(individual)"]),
            "ag": parse_ag(row["Notification to AG"]),
            "penalty": parse_penalty(row["$ Penalty"])
        }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(state_laws, f, indent=2)

    print(f"Saved structured data to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()