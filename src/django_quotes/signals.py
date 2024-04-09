#
# signals.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

"""Defines signals

quote_random_retrieved is emitted when a random quote is supplied.

The `sender` should in most contexts be either `Source` or `SourceGroup`
 class definitions (**not instances**).
The `instance` should be the actual instance of the `Source` that is being used.

This signal will update the `quotes_retrieved` stats in the related ``GroupStats``,
`SourceStats`, and `QuoteStats` objects.
"""

import django.dispatch

quote_random_retrieved = django.dispatch.Signal()
