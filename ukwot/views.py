from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Otter


@login_required
def dashboard_home(request):
    return render(request, "dashboard/home.html", {"active_page": "home"})


class OtterListView(LoginRequiredMixin, ListView):
    model = Otter
    template_name = "otters/otter_list.html"
    context_object_name = "otters"

    def get_queryset(self):
        return (
            Otter.objects
            .select_related("species", "rescue")
            .order_by("otter_id")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        return ctx


class OtterCreateView(LoginRequiredMixin, CreateView):
    model = Otter
    template_name = "otters/otter_form.html"
    fields = ["name", "date_of_birth", "gender", "weight_kg", "status", "arrival_date", "species", "rescue"]
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "create"
        return ctx


class OtterUpdateView(LoginRequiredMixin, UpdateView):
    model = Otter
    template_name = "otters/otter_form.html"
    fields = ["name", "date_of_birth", "gender", "weight_kg", "status", "arrival_date", "species", "rescue"]
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "edit"
        return ctx


class OtterDeleteView(LoginRequiredMixin, DeleteView):
    model = Otter
    template_name = "otters/otter_confirm_delete.html"
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        return ctx