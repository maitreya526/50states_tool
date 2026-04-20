import json


# -----------------------------
# LOAD DATA
# -----------------------------
def load_state_laws(path="data/processed/state_laws.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# PII CHECK (simple version)
# -----------------------------
def is_reportable(state_law, incident):
    # MVP: assume reportable if any data present
    # (you can refine using pii_bucket later)
    return len(incident["data_types"]) > 0


# -----------------------------
# STATE EVALUATION
# -----------------------------
def evaluate_state(state, law, incident):
    users = incident["affected_users"].get(state, 0)

    reportable = is_reportable(law, incident)

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

    for r in results.values():
        if r["individual_deadline_days"] is not None:
            deadlines.append(r["individual_deadline_days"])

        if r["ag_required"]:
            if r["ag_deadline_days"] is not None:
                ag_deadlines.append(r["ag_deadline_days"])

    return {
        "report_all": any(r["reportable"] for r in results.values()),
        "earliest_individual_deadline": min(deadlines) if deadlines else None,
        "earliest_ag_deadline": min(ag_deadlines) if ag_deadlines else None
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