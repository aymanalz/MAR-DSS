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

    def _get_constraint_points(self, response_level: int) -> float:
        """Convert response level to points.
        
        Point system:
        - 0 (Acceptable): 10 points
        - 1 (Cost penalty): 9 points
        - 2 (Warning): 8 points
        - 3 (Mitigation): 7 points
        - 4 (Reject): 0 points
        """
        point_map = {
            0: 10.0,  # Acceptable
            1: 9.0,   # Cost penalty
            2: 8.0,   # Warning
            3: 7.0,   # Mitigation
            4: 0.0    # Reject
        }
        return point_map.get(response_level, 0.0)

    def calculate_type_scores(self) -> Dict[str, float]:
        """
        Calculate type-specific scores for the option.
        
        Scoring system:
        - Constraints: 10 points (acceptable), 9 (cost), 8 (warning), 7 (mitigation), 0 (reject)
        - Benefits: Convert percentage to points (100% = 10 points)
        - Score = (actual_points / ideal_points) × 100%
        
        Returns:
            {
                "hydrogeologic": float (0-100),
                "environmental": float (0-100),
                "regulation": float (0-100)
            }
        """
        # Step 1: Check hard constraints
        for hc in self.hard_constraints:
            if not hc.get("pass", True):
                return {
                    "hydrogeologic": 0.0,
                    "environmental": 0.0,
                    "regulation": 0.0
                }
        
        # Step 2: Group soft constraints by type
        type_constraints = {
            "hydrogeologic": [],
            "environmental": [],
            "regulation": []
        }
        
        for sm in self.soft_metrics:
            constraint_type = sm.get("type", "").lower()
            # Map "regulation" (from "Regulation") to "regulation" for consistency
            # Already lowercased, so just check if it's in our type_constraints
            
            if constraint_type in type_constraints:
                response_level = sm.get("response", 0)
                points = self._get_constraint_points(response_level)
                type_constraints[constraint_type].append(points)
        
        # Step 3: Calculate benefit points
        # Benefits apply to all types
        benefit_points = []
        for bm in self.benefit_metrics:
            benefit_value = bm.get("value", 0.0)  # Normalized [0, 1]
            points = benefit_value * 10.0
            benefit_points.append(points)
        
        # Step 4: Calculate scores for each type
        scores = {}
        num_benefits = len(self.benefit_metrics)
        
        for constraint_type, constraint_points_list in type_constraints.items():
            num_constraints = len(constraint_points_list)
            actual_constraint_points = sum(constraint_points_list)
            actual_benefit_points = sum(benefit_points)
            
            # Calculate ideal points
            ideal_constraint_points = num_constraints * 10.0
            ideal_benefit_points = num_benefits * 10.0
            ideal_total = ideal_constraint_points + ideal_benefit_points
            
            # Calculate actual points
            actual_total = actual_constraint_points + actual_benefit_points
            
            # Calculate score
            if ideal_total > 0:
                type_score = (actual_total / ideal_total) * 100.0
            else:
                # No constraints or benefits - default to 100%
                type_score = 100.0
            
            # Clamp to [0, 100]
            scores[constraint_type] = max(0.0, min(100.0, type_score))
        
        return scores