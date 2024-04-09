#
# test_docs.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

import pytest
from django_quotes import views


# Testing for documented views per: https://simonwillison.net/2018/Jul/28/documentation-unit-tests/
@pytest.mark.xfail
@pytest.mark.parametrize("view_class", [v for v in dir(views) if v.endswith("View")])
def test_view_classes_are_documented(documented_views, view_class):
    assert view_class in documented_views
