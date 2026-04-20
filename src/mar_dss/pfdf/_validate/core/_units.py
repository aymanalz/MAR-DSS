"""
Functions to validate unit conversion options
----------
Functions:
    units       - Checks a unit is supported
    conversion  - validates a units-per-meter conversion factor
"""

from __future__ import annotations

import typing

from mar_dss.pfdf._utils import real
from mar_dss.pfdf._utils.units import supported
from mar_dss.pfdf._validate.core._array import scalar
from mar_dss.pfdf._validate.core._elements import positive
from mar_dss.pfdf._validate.core._low import option

if typing.TYPE_CHECKING:
    from typing import Any, Optional


def units(units: Any, include: Optional[str] = None) -> str:
    "Checks that a unit is supported"
    allowed = supported()
    if include is not None:
        allowed.append(include)
    return option(units, "units", allowed)


def conversion(input: Any, name: str) -> float:
    "Validates a units-per-meter conversion factor"
    if input is not None:
        input = scalar(input, name, real)
        positive(input, name)
    return input
