from engine.rules import load_state_laws, run_engine


laws = load_state_laws()

incident = {
    "data_types": ["email", "biometric"],
    "affected_users": {
        "new_york": 600,
        "arizona": 1200,
        "idaho": 300
    }
}

result = run_engine(incident, laws)

import json
print(json.dumps(result, indent=2))