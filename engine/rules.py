import json


# -----------------------------
# LOAD DATA
# -----------------------------
def load_state_laws(path="data/processed/state_laws.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# PII CATEGORY MAPPING
# -----------------------------
def map_data_types(data_types):
    categories = set()

    for d in data_types:
        d = d.lower()

        # STRONG SIGNALS (almost always trigger)
        if d in ["ssn", "social_security"]:
            categories.add("ssn")

        elif d in ["driver_license", "state_id", "id"]:
            categories.add("id")

        elif d in ["financial", "credit_card", "bank", "account"]:
            categories.add("financial")

        # MEDIUM SIGNALS
        elif d in ["medical", "health"]:
            categories.add("medical")

        elif d in ["biometric"]:
            categories.add("biometric")

        # CREDENTIALS (IMPORTANT VARIATION)
        elif d in ["email_password", "credentials"]:
            categories.add("credentials")

        # WEAK SIGNAL (email alone)
        elif d in ["email"]:
            categories.add("email_only")

    return categories


# -----------------------------
# CHECK IF STATE COVERS DATA
# -----------------------------
def pii_match(pii_text, categories):
    if not pii_text:
        return False

    text = pii_text.lower()
    # Handle generic legal clauses (e.g., "one or more specified data elements")
    generic_phrases = [
        "one or more specified data elements",
        "one or more of the following",
        "one or more data elements"
    ]

    if any(phrase in text for phrase in generic_phrases):
        if any(cat in categories for cat in ["ssn", "id", "financial"]):
            return True

    keyword_map = {
        "ssn": ["ssn", "social security"],
        "id": ["driver", "license", "state id", "identification"],
        "financial": ["account", "credit", "debit", "financial"],
        "medical": ["medical", "health"],
        "biometric": ["biometric", "fingerprint", "iris"],
        "credentials": ["email", "username", "password"]
    }

    # 1. STRONG categories → immediate True
    for cat in ["ssn", "id", "financial", "medical", "biometric"]:
        if cat in categories:
            for keyword in keyword_map[cat]:
                if keyword in text:
                    return True

    # 2. Credentials (email + password type)
    if "credentials" in categories:
        cred_keywords = keyword_map["credentials"]
        if any(k in text for k in cred_keywords):
            return True

    # 3. Email alone → usually NOT sufficient
    # (only trigger if explicitly mentioned WITHOUT password requirement)
    if "email_only" in categories:
        if "email" in text and "password" not in text:
            return True

    return False

# -----------------------------
# PII CHECK (simple version)
# -----------------------------
def is_reportable(state_law, incident):
    # Encryption shortcut
    if incident.get("encrypted") is True:
        return False

    data_categories = map_data_types(incident["data_types"])
    pii_text = state_law.get("meta", {}).get("pii_definition", "")

    result = pii_match(pii_text, data_categories)

    return result
# -----------------------------
# STATE EVALUATION
# -----------------------------
def evaluate_state(state, law, incident):
    users = incident["affected_users"].get(state, 0)

    reportable = is_reportable(law, incident)

    if not reportable:
        return {
            "reportable": False,
            "affected_users": users,
            "individual_deadline_days": None,
            "ag_required": False,
            "ag_deadline_days": None
        }

    # Timeline
    timeline = law["timeline"]
    deadline_days = timeline["days"] if timeline["type"] == "fixed" else None

    # AG
    ag = law["ag"]

    ag_required = False
    ag_deadline_days = None

    if ag["type"] == "mandatory":
        ag_required = True

    elif ag["type"] == "conditional":
        if ag["threshold"] is not None and users >= ag["threshold"]:
            ag_required = True

    if ag_required:
        ag_deadline_days = ag["deadline_days"]

    return {
        "reportable": reportable,
        "affected_users": users,
        "individual_deadline_days": deadline_days,
        "ag_required": ag_required,
        "ag_deadline_days": ag_deadline_days
    }


# -----------------------------
# AGGREGATION (IMPORTANT)
# -----------------------------
def aggregate_results(results):
    deadlines = []
    ag_deadlines = []

    individual_sources = []
    ag_sources = []

    ag_triggered_states = []

    for state, r in results.items():
        # Individual deadlines
        if r["individual_deadline_days"] is not None:
            deadlines.append((r["individual_deadline_days"], state))

        # AG
        if r["ag_required"]:
            ag_triggered_states.append(state)

            if r["ag_deadline_days"] is not None:
                ag_deadlines.append((r["ag_deadline_days"], state))

    # Compute earliest deadlines + source
    earliest_individual = None
    individual_source = None

    if deadlines:
        earliest_individual, individual_source = min(deadlines)

    earliest_ag = None
    ag_source = None

    if ag_deadlines:
        earliest_ag, ag_source = min(ag_deadlines)

    return {
        "report_all": any(r["reportable"] for r in results.values()),

        "earliest_individual_deadline": earliest_individual,
        "individual_source_state": individual_source,

        "earliest_ag_deadline": earliest_ag,
        "ag_source_state": ag_source,

        "states_triggering_ag": ag_triggered_states,
        "num_states": len(results),
        "num_ag_required": len(ag_triggered_states)
    }


# -----------------------------
# MAIN ENGINE
# -----------------------------
def run_engine(incident, laws):
    results = {}

    for state, users in incident["affected_users"].items():
        if state not in laws:
            continue

        results[state] = evaluate_state(state, laws[state], incident)

    aggregate = aggregate_results(results)

    return {
        "per_state": results,
        "aggregate": aggregate
    }