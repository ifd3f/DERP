"""
Generates a bunch of random transactions and fundings.
"""

import random

from datetime import datetime, timedelta, timezone

from erp.models import *

def run():
    iks = make_item_kinds()
    ccs = make_cost_centers()
    now = datetime.now(tz=timezone.utc)

    # Make purchases
    for i in range(0, 1000):
        days_before = random.random() * 365 * 3
        date = now - timedelta(days=days_before)
        Purchase.objects.create(
            purchase_date=date,
            item=random.choice(iks),
            quantity=random.randint(1, 100),
            actual_price=random.random() * 100,
            supplier="https://example.com",
            cost_center=random.choice(ccs)
        )

    # Make fundings
    for i in range(0, 50):
        days_before = random.random() * 365 * 3
        date = now - timedelta(days=days_before)
        Funding.objects.create(
            name="Test Funding",
            funding_date=date,
            cost_center=random.choice(ccs),
            credit=random.random() * 100,
        )

def make_item_kinds():
    items = [
        ItemKind.objects.create(
            name=name,
            description="A test item for generating transactions",
        )
        for name in ["Apple", "Banana", "Pear", "Lemon", "Lime", "Watermelon"]
    ]

    return items


def make_cost_centers():
    cc1 = CostCenter.objects.create(
        name="Slush Fund",
        description="Gay",
    )
    cc2 = CostCenter.objects.create(
        name="Engineering",
        description="Gay",
        parent=cc1,
    )
    cc3 = CostCenter.objects.create(
        name="Chemistry",
        description="Gay",
        parent=cc1,
    )

    return [cc1, cc2, cc3]
