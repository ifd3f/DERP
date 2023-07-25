from django.conf import settings
from django.db import models


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

    purchaser = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)


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
    parent = models.ForeignKey("CostCenter", null=True, on_delete=models.SET_NULL)
