from typing import Any, Dict, List

import mar_dss.app.utils.data_storage as data_storage

# Consider 6 MAR options:
# 1. Surface Recharge
# 2. Dry Well
# 3. Injection Well
# 4. Surface Recharge with Treatment
# 5. Dry Well with Treatment
# 6. Injection Well with Treatment


class MAROption:
    def __init__(self, name: str, base_cost: float, data: Dict[str, Any]):
        self.name = name
        self.base_cost = base_cost
        self.data = data


def mar_options() -> List[MAROption]:
    """Create and return a list of MAR technology options."""
    options = []

    # Surface recharge
    surface_recharge = MAROption(
        name="Surface Recharge", base_cost=1000000, data={}
    )
    options.append(surface_recharge)

    # Dry well
    dry_well = MAROption(name="Dry Well", base_cost=1000000, data={})
    options.append(dry_well)

    # Injection well
    injection_well = MAROption(
        name="Injection Well", base_cost=1000000, data={}
    )
    options.append(injection_well)

    # # Surface recharge with treatment
    # surface_recharge_with_treatment = MAROption(
    #     name="Surface Recharge with Treatment", base_cost=1000000, data={}
    # )
    # options.append(surface_recharge_with_treatment)

    # # Dry well with treatment
    # dry_well_with_treatment = MAROption(
    #     name="Dry Well with Treatment", base_cost=1000000, data={}
    # )
    # options.append(dry_well_with_treatment)

    # # Injection well with treatment
    # injection_well_with_treatment = MAROption(
    #     name="Injection Well with Treatment", base_cost=1000000, data={}
    # )
    # options.append(injection_well_with_treatment)

    return options
