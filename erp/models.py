from typing import List, Iterable, NamedTuple
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Value, ExpressionWrapper, CharField, Sum
from django.db.models.functions import Concat
from django.urls import reverse


MAX_NAME_LENGTH = 64


class Purchase(models.Model):
    """
    A purchase of a kind of item for a project.
    """

    purchase_date = models.DateTimeField()

    comment = models.CharField(max_length=MAX_NAME_LENGTH, null=False, default="")
    item = models.ForeignKey("ItemKind", on_delete=models.PROTECT)

    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    supplier = models.URLField(null=False, default="")

    cost_center = models.ForeignKey("CostCenter", null=False, on_delete=models.PROTECT)

    purchaser = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    create_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.comment or f"{self.item.name} x{self.quantity}"

    def get_absolute_url(self) -> str:
        return reverse('purchase', kwargs={'pk': self.id})


class Funding(models.Model):
    """
    A one-time funding transaction.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    cost_center = models.ForeignKey("CostCenter", null=False, on_delete=models.PROTECT)
    funding_date = models.DateTimeField()
    credit = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.CharField(max_length=MAX_NAME_LENGTH, null=False, default="")

    create_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('funding', kwargs={'pk': self.id})


class ItemKind(models.Model):
    """
    A kind of item.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

    @property
    def url(self) -> str:
        return f"/item-kinds/{self.id}"


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
            nodes = [(self, self.parent.path if self.parent else "/")]
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

    def get_absolute_url(self) -> str:
        return reverse('cost-center', kwargs={'pk': self.id})

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f"Cost Center {self.name} ({self.id})"

    def iter_upwards(self) -> Iterable["CostCenter"]:
        """
        Iterator that goes upwards, starting from this node.
        """
        n = self
        while n is not None:
            yield n
            n = n.parent

    def nav_path(self) -> List["CostCenter"]:
        path = list(self.iter_upwards())
        path.reverse()
        return path

    @property
    def total_balance(self) -> float:
        return (
            self.recursive_fundings.aggregate(b=Sum("credit"))["b"]
            - self.recursive_purchases.aggregate(b=Sum("total_price"))["b"]
        )

    @property
    def recursive_purchases(self):
        return Purchase.objects.filter(cost_center__path__startswith=self.path)

    @property
    def recursive_fundings(self):
        return Funding.objects.filter(cost_center__path__startswith=self.path)

    def query_balance_sheet(self):
        """
        Returns the balance sheet for all transactions in
        this cost center and all of its children.
        """

        purchases = self.recursive_purchases.values(
            t_id=ExpressionWrapper(
                Concat(Value("P"), F("pk")), output_field=CharField()
            ),
            t_date=F("purchase_date"),
            t_name=ExpressionWrapper(
                Concat(F("item__name"), Value(" x"), F("quantity")),
                output_field=CharField(),
            ),
            t_cost_center=F("cost_center__name"),
            t_cost_center_id=F("cost_center__id"),
            t_price=-F("total_price"),
            t_href=ExpressionWrapper(
                Concat(Value("/purchases/"), F("pk")), output_field=CharField()
            ),
        )

        fundings = self.recursive_fundings.values(
            t_id=ExpressionWrapper(
                Concat(Value("F"), F("pk")), output_field=CharField()
            ),
            t_date=F("funding_date"),
            t_name=F("name"),
            t_cost_center=F("cost_center__name"),
            t_cost_center_id=F("cost_center__id"),
            t_price=F("credit"),
            t_href=ExpressionWrapper(
                Concat(Value("/fundings/"), F("pk")), output_field=CharField()
            ),
        )

        return purchases.union(fundings)


class TransactionRow(NamedTuple):
    t_date: datetime
    t_name: str
    t_cost_center: str
    t_cost_center_id: int
    t_price: float
    t_href: str
