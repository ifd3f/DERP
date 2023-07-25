from django.conf import settings
from django.db import models


MAX_NAME_LENGTH = 64


class Purchase(models.Model):
    """
    A purchase of a kind of item for a project.
    """

    purchase_date = models.DateTimeField(auto_now_add=True)

    item = models.ForeignKey("ItemKind", on_delete=models.PROTECT)

    quantity = models.FloatField()
    actual_price = models.FloatField()
    supplier = models.URLField()

    category = models.ForeignKey("Category", on_delete=models.PROTECT)

    purchaser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)


class ItemKind(models.Model):
    """
    A kind of item.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.TextField()


class Category(models.Model):
    """
    A category of purchase.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.TextField()
    parent = models.ForeignKey("Category", null=True, on_delete=models.SET_NULL)
