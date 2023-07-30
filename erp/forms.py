from django import forms

from .models import Purchase


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['purchase_date', 'comment', 'item', 'quantity', 'actual_price', 'supplier', 'cost_center']