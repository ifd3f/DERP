from typing import Iterable, NamedTuple
from datetime import datetime

from django.conf import settings
from django.db import models, transaction
from computedfields.models import (
    ComputedFieldsModel,
    computed,
    precomputed,
    update_computedfields,
)


MAX_NAME_LENGTH = 64


class Purchase(models.Model):
    """
    A purchase of a kind of item for a project.
    """

    purchase_date = models.DateTimeField()

    item = models.ForeignKey("ItemKind", on_delete=models.PROTECT)

    quantity = models.FloatField()
    actual_price = models.FloatField()
    supplier = models.URLField()

    cost_center = models.ForeignKey("CostCenter", null=False, on_delete=models.PROTECT)

    purchaser = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )


class Funding(models.Model):
    """
    A one-time funding transaction.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    cost_center = models.ForeignKey("CostCenter", null=False, on_delete=models.PROTECT)
    funding_date = models.DateTimeField()
    credit = models.FloatField()


class ItemKind(models.Model):
    """
    A kind of item.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.TextField()


class CostCenter(models.Model):
    """
    A cost center for purchases.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.TextField()
    parent = models.ForeignKey(
        "CostCenter", null=True, on_delete=models.SET_NULL, related_name="children"
    )

    path = models.CharField(max_length=128, default="")
    # return str(self.id) if self.parent is None else f"{self.parent.path}/{self.id}"

    def save(self, *args, **kwargs):
        if self.id is None:
            # This is our first call. We cannot have any children.
            # Therefore, save once to generate the ID, then generate the path from the ID.
            with transaction.atomic():
                super().save()
                self.path = (
                    f"/{self.id}"
                    if self.parent is None
                    else f"{self.parent.path}/{self.id}"
                )
                super().save(
                    force_update=True
                )  # Must be an update to prevent double-insert
            return

        # Otherwise, we already know the ID and must update child paths.
        with transaction.atomic():
            visited = []
            nodes = [(self, self.parent.path if self.parent else '/')]
            while nodes:
                n, parent_path = nodes[-1]
                nodes.pop()

                n.path = f"{parent_path}/{n.id}"
                visited.append(n)

                for c in n.children.all():
                    nodes.append((c, n.path))

            for n in visited:
                print(n, n.path)
                models.Model.save(n, force_update=True)

    def __repr__(self):
        return f"Cost Center {self.name} ({self.id})"

    def query_balance_sheet(self) -> Iterable['TransactionRow']:
        """
        Returns the balance sheet for all transactions in
        this cost center and all of its children.
        """

        from django.db.models import F, Value, ExpressionWrapper, CharField, Sum
        from django.db.models.functions import Concat

        purchases = Purchase.objects.filter(
            cost_center__path__startswith=self.path
        ).values(
            t_date=F("purchase_date"),
            t_name=ExpressionWrapper(
                Concat(F("item__name"), Value(" x"), F("quantity")),
                output_field=CharField(),
            ),
            t_cost_center=F("cost_center__name"),
            t_cost_center_id=F("cost_center__id"),
            t_price=-F("actual_price"),
            t_href=ExpressionWrapper(
                Concat(Value("/purchases/"), F("pk")), output_field=CharField()
            ),
        )

        fundings = Funding.objects.filter(
            cost_center__path__startswith=self.path
        ).values(
            t_date=F("funding_date"),
            t_name=F("name"),
            t_cost_center=F("cost_center__name"),
            t_cost_center_id=F("cost_center__id"),
            t_price=F("credit"),
            t_href=ExpressionWrapper(
                Concat(Value("/fundings/"), F("pk")), output_field=CharField()
            ),
        )

        raw_rows = purchases.union(fundings).order_by("t_date")

        # Calculate a cumulative sum
        csum = 0
        for r in raw_rows:
            csum += r["t_price"]
            yield TransactionRow(
                date=r["t_date"],
                name=r["t_name"],
                cost_center=r["t_cost_center"],
                cost_center_id=r["t_cost_center_id"],
                price=r["t_price"],
                href=r["t_href"],
                balance=csum,
            )


class TransactionRow(NamedTuple):
    date: datetime
    name: str
    cost_center: str
    cost_center_id: int
    price: float
    href: str
    balance: float
