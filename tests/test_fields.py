from __future__ import annotations

import astropy.units as u
import pandas as pd
import pytest

from gwresults.fields import mass_1, total_mass, waveform_approximant


@pytest.fixture
def table():
    return pd.DataFrame(
        {
            "event": ["GW150914_095045", "GW170817_120000", "GW190521_030229"],
            "total_mass": [65.0, 2.8, 150.0],
            "mass_1": [36.0, 1.5, 85.0],
            "waveform_approximant": ["SEOBNRv5PHM", "IMRPhenomD", "SEOBNRv5PHM"],
        }
    )


def test_field_comparison_builds_condition():
    condition = total_mass >= 100
    assert condition.column == "total_mass"
    assert condition.value == 100


def test_condition_evaluate_filters_rows(table):
    mask = (total_mass >= 100).evaluate(table)
    assert mask.tolist() == [False, False, True]


def test_condition_with_quantity_converts_units(table):
    mask = (total_mass >= 100 * u.solMass).evaluate(table)
    assert mask.tolist() == [False, False, True]


def test_condition_with_quantity_in_other_compatible_unit(table):
    # 100 solar masses expressed in kg should convert correctly.
    value = (100 * u.solMass).to(u.kg)
    mask = (total_mass >= value).evaluate(table)
    assert mask.tolist() == [False, False, True]


def test_string_equality_condition(table):
    mask = (waveform_approximant == "SEOBNRv5PHM").evaluate(table)
    assert mask.tolist() == [True, False, True]


def test_string_inequality_condition(table):
    mask = (waveform_approximant != "SEOBNRv5PHM").evaluate(table)
    assert mask.tolist() == [False, True, False]


def test_le_condition(table):
    mask = (total_mass <= 65).evaluate(table)
    assert mask.tolist() == [True, True, False]


def test_lt_condition(table):
    mask = (total_mass < 65).evaluate(table)
    assert mask.tolist() == [False, True, False]


def test_gt_condition(table):
    mask = (total_mass > 100).evaluate(table)
    assert mask.tolist() == [False, False, True]


def test_compound_and_condition(table):
    condition = (total_mass >= 100) & (waveform_approximant == "SEOBNRv5PHM")
    mask = condition.evaluate(table)
    assert mask.tolist() == [False, False, True]


def test_compound_or_condition(table):
    condition = (mass_1 >= 85) | (mass_1 <= 2)
    mask = condition.evaluate(table)
    assert mask.tolist() == [False, True, True]


def test_chained_compound_and_condition(table):
    condition = (total_mass >= 1) & (mass_1 >= 1) & (waveform_approximant == "SEOBNRv5PHM")
    mask = condition.evaluate(table)
    assert mask.tolist() == [True, False, True]


def test_chained_compound_or_condition(table):
    condition = (mass_1 >= 1000) | (mass_1 <= 2) | (total_mass >= 100)
    mask = condition.evaluate(table)
    assert mask.tolist() == [False, True, True]


def test_field_is_hashable():
    assert len({total_mass, mass_1}) == 2
