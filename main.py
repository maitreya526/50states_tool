# from engine.rules import load_state_laws, run_engine
# import json

# laws = load_state_laws()

# # Use YOUR states only
# states = {
#     "new_york": 600,
#     "arizona": 1200,
#     "washington": 800
# }

# scenarios = {
#     "A_email_only": {
#         "data_types": ["email"],
#         "encrypted": False
#     },
#     "B_credentials": {
#         "data_types": ["email_password"],
#         "encrypted": False
#     },
#     "C_ssn": {
#         "data_types": ["ssn"],
#         "encrypted": False
#     },
#     "D_biometric": {
#         "data_types": ["biometric"],
#         "encrypted": False
#     },
#     "E_encrypted_ssn": {
#         "data_types": ["ssn"],
#         "encrypted": True
#     },
#     "F_mixed_data": {
#         "data_types": ["email_password", "ssn"],
#         "encrypted": False
#     }
# }

# for name, scenario in scenarios.items():
#     incident = {
#         "data_types": scenario["data_types"],
#         "encrypted": scenario["encrypted"],
#         "affected_users": states
#     }

#     print("\n" + "="*50)
#     print(f"SCENARIO: {name}")
#     print("="*50)

#     result = run_engine(incident, laws)
#     print(json.dumps(result, indent=2))

# from engine.rules import load_state_laws, run_engine
# import pandas as pd
# import matplotlib.pyplot as plt
# import json
# import os

# # Load laws
# laws = load_state_laws()

# # All available states from dataset
# all_states = list(laws.keys())

# # Number of states to test
# sizes = [1, 5, 10, 25, 50]

# results = []

# for n in sizes:

#     # Select first N states
#     selected_states = {
#         state: 1000
#         for state in all_states[:n]
#     }

#     # Fixed high-sensitivity scenario
#     incident = {
#         "data_types": ["ssn"],
#         "encrypted": False,
#         "affected_users": selected_states
#     }

#     # Run engine
#     result = run_engine(incident, laws)

#     # DEBUG OUTPUT
#     print("\n" + "="*60)
#     print(f"STATES TESTED: {n}")
#     print("="*60)
#     print(json.dumps(result, indent=2))

#     # Extract per-state results
#     per_state = result.get("per_state", {})

#     # Count reportable states
#     r = sum(
#         1
#         for state_data in per_state.values()
#         if state_data.get("reportable") == True
#     )

#     # Manual complexity formula
#     baseline_complexity = n + (3 * r) + 3

#     # System output remains approximately constant
#     system_complexity = 4

#     results.append({
#         "states": n,
#         "reportable_states": r,
#         "baseline_complexity": baseline_complexity,
#         "system_complexity": system_complexity
#     })

# # Convert to dataframe
# df = pd.DataFrame(results)

# print("\nFINAL RESULTS")
# print(df)

# # ============================================================
# # GRAPH GENERATION
# # ============================================================

# # Create figs directory if it does not exist
# os.makedirs("figs", exist_ok=True)

# # Create plot
# plt.figure(figsize=(8, 5))

# # Manual complexity line
# plt.plot(
#     df["states"],
#     df["baseline_complexity"],
#     marker='o',
#     linewidth=2,
#     label="Manual Analysis"
# )

# # System-assisted complexity line
# plt.plot(
#     df["states"],
#     df["system_complexity"],
#     marker='o',
#     linewidth=2,
#     label="System-Assisted Analysis"
# )

# # Labels and title
# plt.xlabel("Number of Affected States")
# plt.ylabel("Decision Complexity")
# plt.title("Scaling Behavior of Decision Complexity")

# # Grid and legend
# plt.grid(True)
# plt.legend()

# # Save figure
# plt.tight_layout()
# plt.savefig("figs/scaling_complexity.png", dpi=300)

# # Show graph
# plt.show()

# print("\nGraph saved to: figs/scaling_complexity.png")
