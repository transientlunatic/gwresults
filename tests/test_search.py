from __future__ import annotations

import pytest

from gwresults import search


def test_search_get_not_implemented():
    with pytest.raises(NotImplementedError):
        search.get()
