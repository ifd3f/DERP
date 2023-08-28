from datetime import datetime
from typing import Any, Dict
from django import forms

from .models import ItemKind, Purchase


class PurchaseCreateForm(forms.ModelForm):
    item = forms.CharField()
    comment = forms.CharField(required=False)
    supplier = forms.URLField(required=False)
    purchase_date = forms.DateTimeField(initial=datetime.now)

    def save(self, commit=True):
        purchase: Purchase = super().save(commit=False)
        item, _ = ItemKind.objects.get_or_create(name=self.cleaned_data['item'])
        purchase.item = item
        purchase.comment = self.cleaned_data['comment']
        purchase.supplier = self.cleaned_data['supplier']
        if commit:
            purchase.save()
        return purchase

    class Meta:
        model = Purchase
        fields = [
            "comment",
            "supplier",
            "purchase_date",
            "quantity",
            "total_price",
            "cost_center",
        ]
