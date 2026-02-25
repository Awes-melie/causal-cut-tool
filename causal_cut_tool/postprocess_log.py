import json
import sys
from itertools import product

import pandas as pd

from causal_cut_tool.fault_finding import reproduce_fault


def build_attack(attack: dict):
    if "error" in attack:
        if "treatment_strategies" not in attack:
            assert attack["error"] in [
                "Missing data for control_strategy",
                "No faults observed. P(error) = 0",
            ], f"Bad error {attack['error']} in {attack}"
            # Populate with dummy data if we haven't found anything
            attack["treatment_strategies"] = [{"intervention_index": i} for i in range(len(attack["attack"]))]


    treatment_strategies = [
        (
            treatment_strategy | treatment_strategy["result"]
            if "result" in treatment_strategy
            else treatment_strategy | {"ci_low": [None], "ci_high": [None]}
        )
        for treatment_strategy in attack["treatment_strategies"]
    ]
    treatment_strategies = pd.DataFrame(treatment_strategies)

    # If we've been able to estimate anything, reorder according to causality
    if "ci_low" in treatment_strategies and "ci_high" in treatment_strategies:
        treatment_strategies["ci_low"] = [c[0] for c in treatment_strategies["ci_low"]]
        treatment_strategies["ci_high"] = [c[0] for c in treatment_strategies["ci_high"]]
        treatment_strategies["significant"] = (treatment_strategies["ci_low"] > 1) | (
            treatment_strategies["ci_high"] < 1
        )
        treatment_strategies = treatment_strategies.loc[~treatment_strategies["significant"]]
        treatment_strategies["below_1"] = (1 - treatment_strategies["ci_low"]) / (
            treatment_strategies["ci_high"] - treatment_strategies["ci_low"]
        )
        treatment_strategies["above_1"] = (treatment_strategies["ci_high"] - 1) / (
            treatment_strategies["ci_high"] - treatment_strategies["ci_low"]
        )
        treatment_strategies["rank"] = treatment_strategies[["below_1", "above_1"]].min(axis=1)
        # Sort by rank (low -> high), then last -> first
        treatment_strategies.sort_values(["rank", "intervention_index"], inplace=True, ascending=[True, False])
        # TODO
        # Other potential orderings include swapping rank and intervention index
        # and also sorting first by score, and then merging in the unestimated events by time step
    else:
        # else default to greedy minimal
        treatment_strategies.sort_values("intervention_index", inplace=True, ascending=False)

    interventions = []
    for treatment_strategy in attack["treatment_strategies"]:
        if "result" in treatment_strategy and not (
            treatment_strategy["result"]["ci_low"][0] < 1 < treatment_strategy["result"]["ci_high"][0]
        ):
            interventions.append(attack["attack"][treatment_strategy["intervention_index"]])

    still_fault, _ = reproduce_fault(attack, timesteps=499, interventions=interventions, constants=attack["constants"],)

    # TODO continue importing postprocessing behaviour

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Please provide a JSON log file to process.")

    print(sys.argv[1])
    with open(sys.argv[1]) as f:
        attacks = json.load(f)

    processed_attacks = list(map(build_attack, sorted(attacks, key=lambda a: a["attack_index"])))
    with open(sys.argv[1], "w") as f:
        json.dump(processed_attacks, f)