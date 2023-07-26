from django.shortcuts import render
from typing import NamedTuple
from django.http import HttpResponse
from datetime import datetime
from django.db.models import F, Value, ExpressionWrapper, CharField
from django.db.models.functions import Concat


from .models import Purchase, Funding


class TransactionRow(NamedTuple):
    date: datetime
    name: str
    cost_center: str
    price: float
    balance: float
    href: str


def balance_sheet(request):
    p = (
        Purchase.objects.values()
        .annotate(
            date=F("purchase_date"),
            name=ExpressionWrapper(
                Concat(F("item__name"), Value(" x"), F("quantity")),
                output_field=CharField(),
            ),
            cost_center=F("cost_center__name"),
            price=-F("actual_price"),
            href=ExpressionWrapper(
                Concat(Value("/purchases/"), F("pk")), output_field=CharField()
            ),
        )
        .values("date", "name", "cost_center", "price", "href")
    )
    f = (
        Funding.objects.values()
        .annotate(
            date=F("funding_date"),
            name=F("name"),
            cost_center=F("cost_center__name"),
            price=F("credit"),
            href=ExpressionWrapper(
                Concat(Value("/fundings/"), F("pk")), output_field=CharField()
            ),
        )
        .values("date", "name", "cost_center", "price", "href")
    )
    qs = p.union(f).order_by("date")

    csum = 0
    rows = []
    for r in qs:
        csum += r["price"]
        rows.append(TransactionRow(**r, balance=csum))
    return render(request, "balance_sheet.html", {"transactions": rows})
