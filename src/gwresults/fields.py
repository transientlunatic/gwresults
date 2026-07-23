"""
A tiny expression DSL for querying the summary-statistics table.

`Field` instances stand in for columns of the summary-statistics table
(see `gwresults.stats.load_summary_table`). Comparing a `Field` builds a
`Condition` object rather than evaluating immediately, so conditions can
be composed with ``&``/``|`` and evaluated later, e.g.::

    from gwresults.fields import total_mass, waveform_approximant
    total_mass >= 100 * u.solMass
    (total_mass >= 100 * u.solMass) & (waveform_approximant == "SEOBNRv5PHM")
"""

from __future__ import annotations

import operator
from typing import Callable

import pandas as pd

try:
    import astropy.units as u

    _Quantity = u.Quantity
except ImportError:  # pragma: no cover
    _Quantity = ()


class Condition:
    """
    A single comparison between a column and a value.

    Parameters
    ----------
    column : str
        Name of the summary-statistics column being compared.
    op : callable
        A two-argument comparison function, e.g. `operator.ge`.
    value : object
        The value to compare against. May be an `astropy.units.Quantity`.
    unit : astropy.units.Unit, optional
        The unit the table column is stored in. If ``value`` is a
        `~astropy.units.Quantity`, it is converted to this unit before
        comparison.
    """

    def __init__(self, column: str, op: Callable, value: object, unit=None):
        self.column = column
        self.op = op
        self.value = value
        self.unit = unit

    def evaluate(self, table: pd.DataFrame) -> pd.Series:
        """
        Apply this condition to a summary-statistics table.

        Parameters
        ----------
        table : pandas.DataFrame
            Table containing at least the ``self.column`` column.

        Returns
        -------
        pandas.Series
            Boolean mask of rows satisfying the condition.

        Raises
        ------
        astropy.units.UnitConversionError
            If ``value`` is a `~astropy.units.Quantity` with a unit that
            cannot be converted to this condition's column unit.
        """
        value = self.value
        if isinstance(value, _Quantity):
            value = value.to_value(self.unit) if self.unit is not None else value.value
        return self.op(table[self.column], value)

    def __and__(self, other: Condition) -> CompoundCondition:
        return CompoundCondition(self, other, pd.Series.__and__)

    def __or__(self, other: Condition) -> CompoundCondition:
        return CompoundCondition(self, other, pd.Series.__or__)


class CompoundCondition:
    """
    Two conditions joined by a boolean operator.

    Parameters
    ----------
    left, right : Condition or CompoundCondition
        The conditions being combined.
    op : callable
        A two-argument boolean operator, e.g. `pandas.Series.__and__`.
    """

    def __init__(self, left, right, op: Callable):
        self.left = left
        self.right = right
        self.op = op

    def evaluate(self, table: pd.DataFrame) -> pd.Series:
        """
        Apply this compound condition to a summary-statistics table.

        Parameters
        ----------
        table : pandas.DataFrame
            Table to evaluate the condition against.

        Returns
        -------
        pandas.Series
            Boolean mask of rows satisfying the condition.
        """
        return self.op(self.left.evaluate(table), self.right.evaluate(table))

    def __and__(self, other) -> CompoundCondition:
        return CompoundCondition(self, other, pd.Series.__and__)

    def __or__(self, other) -> CompoundCondition:
        return CompoundCondition(self, other, pd.Series.__or__)


class Field:
    """
    A named column in the summary-statistics table.

    Parameters
    ----------
    column : str
        Name of the column this field refers to.
    unit : astropy.units.Unit, optional
        The unit the column is stored in, used to convert
        `~astropy.units.Quantity` values passed to comparisons.
    """

    def __init__(self, column: str, unit=None):
        self.column = column
        self.unit = unit

    def __ge__(self, value) -> Condition:
        return Condition(self.column, operator.ge, value, self.unit)

    def __le__(self, value) -> Condition:
        return Condition(self.column, operator.le, value, self.unit)

    def __gt__(self, value) -> Condition:
        return Condition(self.column, operator.gt, value, self.unit)

    def __lt__(self, value) -> Condition:
        return Condition(self.column, operator.lt, value, self.unit)

    def __eq__(self, value) -> Condition:  # type: ignore[override]
        return Condition(self.column, operator.eq, value, self.unit)

    def __ne__(self, value) -> Condition:  # type: ignore[override]
        return Condition(self.column, operator.ne, value, self.unit)

    def __hash__(self) -> int:
        return hash(self.column)


_solar_mass = u.solMass if _Quantity else None

event = Field("event")
catalogue = Field("catalogue")
waveform_approximant = Field("waveform_approximant")
total_mass = Field("total_mass", unit=_solar_mass)
chirp_mass = Field("chirp_mass", unit=_solar_mass)
mass_1 = Field("mass_1", unit=_solar_mass)
mass_2 = Field("mass_2", unit=_solar_mass)
