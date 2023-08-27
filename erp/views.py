from datetime import datetime, timezone
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView

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

    transactions = cc.query_balance_sheet().order_by("t_date")

    return render(
        request,
        "cost_center.html",
        {"page_title": cc.name, "cost_center": cc, "transactions": transactions},
    )


class PurchasesListView(ListView):
    model = Purchase
    context_object_name = "purchases"
    queryset = Purchase.objects.order_by("-purchase_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Purchases"
        return context


class PurchaseDetailView(DetailView):
    model = Purchase
    context_object_name = "purchase"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Purchase: {self.object}"
        return context


class PurchaseCreateView(CreateView):
    model = Purchase
    fields = ["name"]


class PurchaseUpdateView(UpdateView):
    model = Purchase
    fields = ["name"]


class PurchaseDeleteView(DeleteView):
    model = Purchase
    success_url = reverse_lazy("purchases")
