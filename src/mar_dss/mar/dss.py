from typing import Any, Dict, List

class DecisionSupportSystem:
    """
    Generic rule-based Decision Support System (DSS).

    Features:
    - Hard-constraint feasibility screening
    - Soft-metric response logic (cost penalties, warnings, mitigations, rejection)
    - Benefit aggregation
    - Deterministic decision classification

    Response levels for soft metrics:
        0 = Normal
        1 = Cost penalty
        2 = Warning
        3 = Mitigation required
        4 = Reject
    """

    def __init__(
        self,
        hard_constraints: List[Dict[str, bool]],
        soft_metrics: List[Dict[str, Any]],
        benefit_metrics: List[Dict[str, float]],
    ):
        """
        hard_constraints:
            [{ "name": str, "pass": bool }]

        soft_metrics:
            [{
                "name": str,
                "response": int,   # 0–4
                "penalty": float
            }]

        benefit_metrics:
            [{
                "name": str,
                "value": float,    # normalized [0,1]
                "weight": float
            }]
        """
        self.hard_constraints = hard_constraints
        self.soft_metrics = soft_metrics
        self.benefit_metrics = benefit_metrics

    def evaluate(self, option) -> Dict[str, Any]:
        """
        Evaluate a single alternative.

        option must define:
            option.base_cost
            option.data (dict-like)
        """

        # ---------- 1. Hard-constraint screening ----------
        for hc in self.hard_constraints:
            if not hc["pass"]:
                return {
                    "status": "Rejected",
                    "cost": [],
                    "benefit_score": 0.0,
                    "warnings": [],
                    "mitigations": [],
                }

        # ---------- 2. Initialization ----------
        cost = []
        warnings = []
        mitigations = []

        # ---------- 3. Soft-metric evaluation ----------
        for sm in self.soft_metrics:
            level = sm["response"]

            #mandatory = False → behaves soft
            #mandatory = True → violation becomes hard rejection
            """
            Hard + acceptable	->allowed
            Hard + Warning	->Rejected
            Hard + Mitigation	-> Rejected
            Hard + Reject	-> Rejected
            Soft + Warning	Allowed
            Soft + Mitigation	Allowed
            Soft + Reject	rejected
            """

             # ---------- Promotion to hard constraint ----------
            if sm.get("hard", True) and level >= 2:
                return {
                    "status": "Rejected",
                    "cost": option.base_cost,
                    "benefit_score": 0.0,
                    "warnings": [],
                    "mitigations": [],
                }

            if level >= 1:
                cost += sm["penalty"]

            if level == 2:
                warnings.append(sm["name"])

            elif level == 3:
                mitigations.append(sm["name"])

            elif level == 4:
                return {
                    "status": "Rejected",
                    "cost": cost,
                    "benefit_score": 0.0,
                    "warnings": warnings,
                    "mitigations": mitigations,
                }

        # ---------- 4. Benefit aggregation ----------
        benefit_score = sum(
            bm["weight"] * bm["value"]
            for bm in self.benefit_metrics
        )

        # ---------- 5. Decision classification ----------
        if mitigations:
            status = "Conditionally Recommended"
        elif warnings:
            status = "Recommended with Warnings"
        else:
            status = "Recommended"

        return {
            "status": status,
            "cost": cost,
            "benefit_score": benefit_score,
            "warnings": warnings,
            "mitigations": mitigations,
        }
