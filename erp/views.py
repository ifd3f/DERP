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


class CostCenterListView(ListView):
    model = CostCenter
    context_object_name = "root_cost_centers"
    queryset = CostCenter.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Cost Centers"
        return context


class CostCenterDetailView(DetailView):
    model = CostCenter
    context_object_name = "cost_center"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = self.object.query_balance_sheet().order_by("t_date")
        context["page_title"] = f"Cost Center: {self.object.name}"
        return context


class PurchaseDetailView(DetailView):
    model = Purchase
    context_object_name = "purchase"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Purchase: {self.object}"
        return context


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
