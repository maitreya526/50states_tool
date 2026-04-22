# 📘 Breach Notification Compliance Engine

## Overview
Rule-based engine to evaluate **multi-state data breach laws** and compute unified compliance requirements.  
Takes incident input → outputs per-state obligations + aggregated deadlines.

---

## 📂 Structure
50states/
├── main.py
├── engine/
│ └── rules.py
├── data/
│ └── processed/
│ └── state_laws.json


### File Roles
- **main.py** → Runs the engine on a sample incident and prints results  
- **engine/rules.py** → Core logic (PII check, timeline, AG rules, aggregation)  
- **data/processed/state_laws.json** → Structured dataset of state laws  

---

## ▶️ Usage

```bash
python main.py
```
---

## Input (Example)
incident = {
    "data_types": ["ssn"],
    "encrypted": False,
    "affected_users": {
        "new_york": 600,
        "arizona": 1200,
        "washington": 800
    }
}

---

## Output
Per-state: reportability, deadlines, AG requirements
Aggregate: earliest deadlines + triggering states
