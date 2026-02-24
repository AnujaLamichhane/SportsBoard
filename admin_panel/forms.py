from django import forms
from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):

    class Meta:
        model = SiteSettings
        fields = "__all__"

        widgets = {
            "maintenance_mode": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }