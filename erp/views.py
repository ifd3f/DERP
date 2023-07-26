from django.shortcuts import render
from typing import NamedTuple
from django.http import Http404, HttpRequest, HttpResponse
from datetime import datetime
from django.db.models import F, Value, ExpressionWrapper, CharField, Sum
from django.db.models.functions import Concat
from .models import CostCenter, Purchase, Funding


class TransactionRow(NamedTuple):
    date: datetime
    name: str
    cost_center: str
    cost_center_id: int
    price: float
    balance: float
    href: str


def home(request: HttpRequest):
    root_cost_centers = CostCenter.objects.filter(parent__isnull=True)
    return render(
        request,
        "home.html",
        {"page_title": "Home", "root_cost_centers": root_cost_centers},
    )


def cost_center(request: HttpRequest, i: int):
    try:
        cc = CostCenter.objects.get(id=i)
    except CostCenter.DoesNotExist:
        raise Http404

    transactions = query_balance_sheet(cc)

    return render(
        request,
        "cost_center.html",
        {"page_title": cc.name, "cost_center": cc, "transactions": transactions},
    )


def query_balance_sheet(root_cost_center: CostCenter):
    """
    Given a root cost center, returns the balance sheet for all transactions in
    that cost center and all of its children.
    """

    purchases = (
        Purchase.objects.filter(cost_center__path__startswith=root_cost_center.path)
        .values()
        .annotate(
            date=F("purchase_date"),
            name=ExpressionWrapper(
                Concat(F("item__name"), Value(" x"), F("quantity")),
                output_field=CharField(),
            ),
            cost_center=F("cost_center__name"),
            cost_center_id=F("cost_center__id"),
            price=-F("actual_price"),
            href=ExpressionWrapper(
                Concat(Value("/purchases/"), F("pk")), output_field=CharField()
            ),
        )
        .values("date", "name", "cost_center", "cost_center_id", "price", "href")
    )

    fundings = (
        Funding.objects.filter(cost_center__path__startswith=root_cost_center.path)
        .annotate(
            date=F("funding_date"),
            name=F("name"),
            cost_center=F("cost_center__name"),
            cost_center_id=F("cost_center__id"),
            price=F("credit"),
            href=ExpressionWrapper(
                Concat(Value("/fundings/"), F("pk")), output_field=CharField()
            ),
        )
        .values("date", "name", "cost_center", "cost_center_id", "price", "href")
    )

    raw_rows = purchases.union(fundings).order_by("date")

    # Calculate a cumulative sum
    csum = 0
    rows = []
    for r in raw_rows:
        csum += r["price"]
        rows.append(TransactionRow(**r, balance=csum))

    return rows
