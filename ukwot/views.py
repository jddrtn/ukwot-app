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
    """
    Allows permanent deletion ONLY if the otter's status is 'Released'.
    This enforces a business rule that active otters cannot be removed.
    """
    model = Otter
    template_name = "otters/otter_confirm_delete.html"
    success_url = reverse_lazy("otter_list")

    def post(self, request, *args, **kwargs):
        """
        Override default delete behaviour to enforce status rule
        and handle foreign key integrity errors.
        """
        self.object = self.get_object()

        # Business rule: only released otters can be deleted
        if self.object.status != "Released":
            messages.error(
                request,
                "Only otters with status 'Released' can be permanently deleted."
            )
            return redirect("otter_list")

        try:
            return super().post(request, *args, **kwargs)

        except IntegrityError:
            # This catches cases where related clinical records still exist
            messages.error(
                request,
                "This otter cannot be deleted because related records exist "
                "(e.g., health assessments)."
            )
            return redirect("otter_list")