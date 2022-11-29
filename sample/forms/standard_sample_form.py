from django import forms
from django.forms import Form, ModelForm
from django.forms.widgets import DateInput

from sample.models import Standard


class StandardForm(ModelForm):
    class Meta:
        model = Standard
        fields = [
            "date_of_collection",
            "matrix",
            "dilution_factor",
            "expected_concentration",
            "observed_concentration",
        ]
        widgets = {
            "date_of_collection": DateInput(
                format=(r"%Y-%m-%d"),
                attrs={
                    "class": "form-control",
                    "placeholder": "Select a date",
                    "type": "date",
                },
            ),
        }


class SlideImagesForm(Form):
    images = forms.ImageField(
        widget=forms.FileInput(attrs={"multiple": True}),
        help_text="Select 15 slide images.",
    )

    def clean_images(self):
        files = self.files.getlist('images')
        if len(files) != 15:
            raise forms.ValidationError("Please upload exactly 15 images.")
        return files
