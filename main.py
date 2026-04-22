from engine.rules import load_state_laws, run_engine
import json

laws = load_state_laws()

# Use YOUR states only
states = {
    "new_york": 600,
    "arizona": 1200,
    "washington": 800
}

scenarios = {
    "A_email_only": {
        "data_types": ["email"],
        "encrypted": False
    },
    "B_credentials": {
        "data_types": ["email_password"],
        "encrypted": False
    },
    "C_ssn": {
        "data_types": ["ssn"],
        "encrypted": False
    },
    "D_biometric": {
        "data_types": ["biometric"],
        "encrypted": False
    },
    "E_encrypted_ssn": {
        "data_types": ["ssn"],
        "encrypted": True
    },
    "F_mixed_data": {
        "data_types": ["email_password", "ssn"],
        "encrypted": False
    }
}

for name, scenario in scenarios.items():
    incident = {
        "data_types": scenario["data_types"],
        "encrypted": scenario["encrypted"],
        "affected_users": states
    }

    print("\n" + "="*50)
    print(f"SCENARIO: {name}")
    print("="*50)

    result = run_engine(incident, laws)
    print(json.dumps(result, indent=2))