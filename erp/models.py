from django.conf import settings
from django.db import models
from computedfields.models import ComputedFieldsModel, computed, compute


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


class CostCenter(ComputedFieldsModel):
    """
    A cost center for purchases.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.TextField()
    parent = models.ForeignKey("CostCenter", null=True, on_delete=models.SET_NULL, related_name='children')

    @computed(models.CharField(max_length=128), depends=[("self", ["parent", "id"])])
    def path(self):
        """
        A string of ID's separated by slashes.

        This improves efficiency for computing recursive cost centers.
        """
        return str(self.id) if self.parent is None else f"{self.parent.id}/{self.id}"
