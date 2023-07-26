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