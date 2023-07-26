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
    href: str
    balance: float


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

    purchases = Purchase.objects.filter(
        cost_center__path__startswith=root_cost_center.path
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
        cost_center__path__startswith=root_cost_center.path
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
    rows = []
    for r in raw_rows:
        csum += r["t_price"]
        rows.append(
            TransactionRow(
                date=r["t_date"],
                name=r["t_name"],
                cost_center=r["t_cost_center"],
                cost_center_id=r["t_cost_center_id"],
                price=r["t_price"],
                href=r["t_href"],
                balance=csum,
            )
        )

    return rows
