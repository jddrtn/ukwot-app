from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError, models
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Otter, HealthAssessment
from .forms import OtterForm, MedicalRecordForm
from django.http import HttpResponse


@login_required
def dashboard_home(request):
    """
    Dashboard landing page.
    """
    total_otter_count = Otter.objects.count()
    released_otter_count = Otter.objects.filter(status="Released").count()
    recent_otters = Otter.objects.select_related("species").order_by("-otter_id")[:5]

    return render(
        request,
        "dashboard/home.html",
        {
            "active_page": "home",
            "total_otter_count": total_otter_count,
            "released_otter_count": released_otter_count,
            "recent_otters": recent_otters,
        },
    )


class OtterListView(LoginRequiredMixin, ListView):
    """
    Otter list with search/sort/filter + pagination.
    """
    model = Otter
    template_name = "otters/otter_list.html"
    context_object_name = "otters"
    paginate_by = 10

    def get_queryset(self):
        """
        Return filtered/sorted otters.
        """
        queryset = Otter.objects.select_related("species")

        released_only = (self.request.GET.get("released") == "1")
        if released_only:
            queryset = queryset.filter(status="Released")

        q = (self.request.GET.get("q") or "").strip()
        if q:
            queryset = queryset.filter(
                models.Q(name__icontains=q) |
                models.Q(species__common_name__icontains=q)
            )

        sort = self.request.GET.get("sort", "otter_id")
        allowed_sort_fields = {
            "otter_id": "otter_id",
            "name": "name",
            "species": "species__common_name",
            "status": "status",
        }
        order_field = allowed_sort_fields.get(sort, "otter_id")

        return queryset.order_by(order_field)

    def get_context_data(self, **kwargs):
        """
        Add query state for template controls.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["sort"] = self.request.GET.get("sort", "otter_id")
        ctx["released_only"] = (self.request.GET.get("released") == "1")
        return ctx


class OtterCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new otter record.
    """
    model = Otter
    template_name = "otters/otter_form.html"
    form_class = OtterForm
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        """
        Add page mode and sidebar state.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "create"
        return ctx


class OtterUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edit an otter record.
    """
    model = Otter
    template_name = "otters/otter_form.html"
    form_class = OtterForm
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        """
        Add page mode and sidebar state.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "edit"
        return ctx


class OtterDeleteView(LoginRequiredMixin, DeleteView):
    """
    Permanently deletes an otter only if status is Released.
    """
    model = Otter
    template_name = "otters/otter_confirm_delete.html"
    success_url = reverse_lazy("otter_list")

    def post(self, request, *args, **kwargs):
        """
        Enforce delete business rule and catch FK errors.
        """
        self.object = self.get_object()

        if self.object.status != "Released":
            messages.error(
                request,
                "Only otters with status 'Released' can be permanently deleted."
            )
            return redirect("otter_list")

        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError:
            messages.error(
                request,
                "This otter cannot be deleted because related records exist "
                "(e.g., health assessments)."
            )
            return redirect("otter_list")


class MedicalRecordListView(LoginRequiredMixin, ListView):
    """
    List view for medical records.
    """
    model = HealthAssessment
    template_name = "medical_records/medical_record_list.html"
    context_object_name = "records"
    paginate_by = 10

    def get_queryset(self):
        """
        Load related otter data and optionally search by otter name.
        """
        queryset = HealthAssessment.objects.select_related("otter").order_by("-assessment_id")

        q = (self.request.GET.get("q") or "").strip()
        if q:
            queryset = queryset.filter(otter__name__icontains=q)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add sidebar state and search state for the template.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "medical_records"
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        return ctx


class MedicalRecordCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new medical record.
    """
    model = HealthAssessment
    form_class = MedicalRecordForm
    template_name = "medical_records/medical_record_form.html"
    success_url = reverse_lazy("medical_record_list")

    def form_valid(self, form):
        """
        Save the health assessment, then optionally update the base otter
        weight if a new assessment weight was entered.
        """
        response = super().form_valid(form)

        if form.instance.weight_kg is not None:
            form.instance.otter.weight_kg = form.instance.weight_kg
            form.instance.otter.save(update_fields=["weight_kg"])

        return response

    def get_context_data(self, **kwargs):
        """
        Add page mode and sidebar state.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "medical_records"
        ctx["mode"] = "create"
        return ctx


class MedicalRecordUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edit an existing medical record.
    """
    model = HealthAssessment
    form_class = MedicalRecordForm
    template_name = "medical_records/medical_record_form.html"
    success_url = reverse_lazy("medical_record_list")

    def form_valid(self, form):
        """
        Save changes, then optionally update the linked otter weight
        to match the assessment weight.
        """
        response = super().form_valid(form)

        if form.instance.weight_kg is not None:
            form.instance.otter.weight_kg = form.instance.weight_kg
            form.instance.otter.save(update_fields=["weight_kg"])

        return response

    def get_context_data(self, **kwargs):
        """
        Add page mode and sidebar state.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "medical_records"
        ctx["mode"] = "edit"
        return ctx

class MedicalRecordDeleteView(LoginRequiredMixin, DeleteView):
    """
    Permanently deletes a medical record.
    """
    model = HealthAssessment
    template_name = "medical_records/medical_record_confirm_delete.html"
    success_url = reverse_lazy("medical_record_list")

    def post(self, request, *args, **kwargs):
        """
        Handle POST delete requests for a medical record.
        """
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Adds 'active_page' to the template context so the sidebar can highlight
        the current section
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "medical_records"
        return ctx