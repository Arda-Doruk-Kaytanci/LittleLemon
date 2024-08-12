from django import forms
from django.contrib.auth.models import User
from .models import Order


class AssignOrderForm(forms.Form):
    order_id = forms.IntegerField(label="Order ID")
    username = forms.CharField(max_length=150, label="Delivery Person Username")

    def clean(self):
        cleaned_data = super().clean()
        order_id = cleaned_data.get("order_id")
        username = cleaned_data.get("username")

        if order_id and username:
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError("The delivery person does not exist.")

            try:
                Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                raise forms.ValidationError("The order does not exist.")
