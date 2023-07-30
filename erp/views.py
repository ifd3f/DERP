from datetime import datetime, timezone
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render

from erp.forms import PurchaseForm

from .models import CostCenter, Purchase


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

    transactions = list(cc.query_balance_sheet())

    return render(
        request,
        "cost_center.html",
        {"page_title": cc.name, "cost_center": cc, "transactions": transactions},
    )


@transaction.atomic
def create_purchase(request: HttpRequest):
    if request.method == "POST":
        form = PurchaseForm(request.POST)

        if form.is_valid():
            purchase = form.save()
            return HttpResponseRedirect(purchase.url)

    else:
        form = PurchaseForm(
            initial={"purchase_date": datetime.now(tz=timezone.utc), "quantity": 1}
        )

    return render(
        request, "create_purchase.html", {"page_title": "Create purchase", "form": form}
    )


def view_purchase(request: HttpRequest, i: int):
    try:
        purchase = Purchase.objects.get(id=i)
    except PurchaseForm.DoesNotExist:
        raise Http404

    return render(
        request,
        "view_purchase.html",
        {"page_title": f"Purchase: {purchase}", "purchase": purchase},
    )
