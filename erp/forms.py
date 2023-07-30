from django import forms

from .models import ItemKind, Purchase


class PurchaseForm(forms.ModelForm):
    template_name = "purchase_form.html"

    item = forms.CharField()
    comment = forms.CharField(required=False)
    supplier = forms.URLField(required=False)

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
            "purchase_date",
            "quantity",
            "actual_price",
            "cost_center",
        ]
