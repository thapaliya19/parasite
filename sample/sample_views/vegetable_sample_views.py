from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from view_breadcrumbs import (
    BaseBreadcrumbMixin,
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
)

from address.forms import AddressForm
from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, SLIDE_COUNT
from sample.forms.standard_sample_form import SlideImagesForm
from sample.forms.vegetable_sample_forms import VegetableForm
from sample.models import Slide, SlideImage, Vegetable
from sample.utils import create_sample_id


# Create your views here
class VegetableListView(LoginRequiredMixin, ListView):
    queryset = Vegetable.objects.order_by("-id")
    template_name: str = "sample/sample_home.html"
    context_object_name = "latest_samples_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sample_type"] = "vegetable"
        return context


class VegetableFormView(LoginRequiredMixin, CreateBreadcrumbMixin, FormView):
    sample_form_class = VegetableForm
    address_form_class = AddressForm
    template_name = "sample/vegetable_sample/vegetable_create.html"
    success_url = reverse_lazy("sample:vegetable_list")
    crumbs = [("Vegetable", success_url), ("New", "")]
    add_home = False

    def get(self, request, *args, **kwargs):
        sample_form = self.sample_form_class()
        address_form = self.address_form_class()
        return render(
            request,
            self.template_name,
            {"sample_form": sample_form, "address_form": address_form},
        )

    def post(self, request, *args, **kwargs):
        sample_form = self.sample_form_class(request.POST, request.FILES)
        address_form = self.address_form_class(request.POST)
        if sample_form.is_valid() and address_form.is_valid():
            vegetable_sample = sample_form.save(commit=False)
            vegetable_sample.user = request.user
            vegetable_sample.site = address_form.cleaned_data.get("municipality")
            vegetable_sample.ward = address_form.cleaned_data.get("ward")
            vegetable_sample.locality = address_form.cleaned_data.get("locality")
            vegetable_sample.sample_id = create_sample_id(
                "vegetable", vegetable_sample.date_of_collection, vegetable_sample.site
            )
            print(f"Saving sample {vegetable_sample}")
            vegetable_sample.save()
            for i in range(1, SLIDE_COUNT + 1):
                slide = Slide(vegetable_sample=vegetable_sample, slide_number=i)
                slide.save()
                for j in range(1, IMAGE_COUNT + 1):
                    for image_type, _ in IMAGE_TYPE_CHOICES:
                        slide_image = SlideImage(
                            uploaded_by=vegetable_sample.user,
                            slide=slide,
                            image="",
                            image_type=image_type,
                            image_id=f"{vegetable_sample}_S{i}_I{j}_{image_type}",
                            image_number=j,
                        )
                        slide_image.save()
            print(f"Finished creating sample {vegetable_sample}")
            messages.success(request, f"Added new vegetable sample {vegetable_sample}.")
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"sample_form": sample_form, "address_form": address_form},
        )


class VegetableDetailView(LoginRequiredMixin, DetailBreadcrumbMixin, DetailView):
    template_name = "sample/vegetable_sample/vegetable_detail.html"
    slug_url_kwarg = "sample_id"
    slug_field = "sample_id"
    context_object_name = "sample"
    model = Vegetable
    breadcrumb_use_pk = False
    add_home = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slides = Slide.objects.filter(vegetable_sample=self.get_object())
        for slide in slides:
            slide.smartphone_images_count = SlideImage.objects.filter(
                ~Q(image=""), slide=slide.id, image_type="S"
            ).count()
            slide.brightfield_images_count = SlideImage.objects.filter(
                ~Q(image=""), slide=slide.id, image_type="B"
            ).count()
        context["slides"] = slides
        context["sample_type"] = "vegetable"
        return context


class VegetableSlideImageCreateView(LoginRequiredMixin, BaseBreadcrumbMixin, FormView):
    template_name = "sample/slide_create.html"
    form_class = SlideImagesForm
    success_url = reverse_lazy("sample:vegetable_list")
    crumbs = [
        ("Vegetable", reverse_lazy("sample:vegetable_list")),
    ]  # OR reverse_lazy
    add_home = False

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Vegetable", reverse_lazy("sample:vegetable_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:vegetable_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
            ("create", ""),
        ]
        self.success_url = reverse_lazy(
            "sample:vegetable_slide_image",
            kwargs={
                "sample_id": self.kwargs["sample_id"],
                "slide_number": self.kwargs["slide_number"],
                "image_type": self.kwargs["image_type"],
            },
        )
        return super(VegetableSlideImageCreateView, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        if self.kwargs["image_type"] not in ["smartphone", "brightfield"]:
            raise Http404(
                f"Image type {self.kwargs['image_type']} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
            )
        if self.kwargs["slide_number"] < 1 or self.kwargs["slide_number"] > 3:
            raise Http404(
                f"Slide number {self.kwargs['slide_number']} is not valid. Valid slide numbers: (1, 2, 3)"
            )
        try:
            vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        except Vegetable.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = get_object_or_404(
            Slide,
            vegetable_sample=vegetable_sample,
            slide_number=int(self.kwargs["slide_number"]),
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_id"] = self.kwargs["sample_id"]
        context["sample_type"] = "vegetable"
        print(context["slide"])
        return context

    def form_valid(self, form, **kwargs):
        vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        slide = get_object_or_404(
            Slide,
            vegetable_sample=vegetable_sample,
            slide_number=int(self.kwargs["slide_number"]),
        )
        db_image_type = "B" if self.kwargs["image_type"] == "brightfield" else "S"
        db_images = SlideImage.objects.all().filter(
            slide=slide,
            image_type=db_image_type,
        )
        files = self.request.FILES.getlist("images")
        for file, image in zip(files, db_images):
            print(file)
            slide_image = SlideImage(
                pk=image.pk,
                uploaded_by=self.request.user,
                slide=image.slide,
                image=ImageFile(file),
                image_id=image.image_id,
                image_number=image.image_number,
                image_type=db_image_type,
            )
            slide_image.save()
        messages.success(self.request, "Successfully added images.")
        return super().form_valid(form)


class VegetableSlideImageDetailView(LoginRequiredMixin, BaseBreadcrumbMixin, ListView):
    template_name = "sample/slide_detail.html"
    breadcrumb_use_pk = False
    crumbs = [
        ("Vegetable", reverse_lazy("sample:vegetable_list")),
    ]  # OR reverse_lazy
    context_object_name = "images"
    add_home = False

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Vegetable", reverse_lazy("sample:vegetable_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:vegetable_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
        ]
        return super(VegetableSlideImageDetailView, self).dispatch(
            request, *args, **kwargs
        )

    def get_queryset(self):
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        if self.kwargs["image_type"] not in ["smartphone", "brightfield"]:
            raise Http404(
                f"Image type {self.kwargs['image_type']} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
            )
        if self.kwargs["slide_number"] < 1 or self.kwargs["slide_number"] > 3:
            raise Http404(
                f"Slide number {self.kwargs['slide_number']} is not valid. Valid slide numbers: (1, 2, 3)"
            )
        try:
            vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        except Vegetable.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        db_image_type = "B" if self.kwargs["image_type"] == "brightfield" else "S"

        slide = Slide.objects.get(
            vegetable_sample=vegetable_sample, slide_number=self.kwargs["slide_number"]
        )
        return SlideImage.objects.all().filter(
            slide=slide,
            image_type=db_image_type,
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        try:
            vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        except Vegetable.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = Slide.objects.get(
            vegetable_sample=vegetable_sample, slide_number=self.kwargs["slide_number"]
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_type"] = "vegetable"
        return context