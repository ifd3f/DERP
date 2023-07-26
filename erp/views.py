from django.shortcuts import render
from django.http import Http404, HttpRequest, HttpResponse
from .models import CostCenter, Purchase, Funding


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
