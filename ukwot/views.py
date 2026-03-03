from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Otter


@login_required
def dashboard_home(request):
    """
    Dashboard landing page.
    Requires login so unauthenticated users are redirected to LOGIN_URL.
    """
    return render(request, "dashboard/home.html", {"active_page": "home"})


class OtterListView(LoginRequiredMixin, ListView):
    """
    Lists all otters in the system (including Released).
    When an otter is permanently deleted, it disappears automatically
    because the row no longer exists in the database.
    """
    model = Otter
    template_name = "otters/otter_list.html"
    context_object_name = "otters"

    def get_queryset(self):
        """
        Return all otters, with related Species/RescueCase preloaded
        to reduce additional database queries.
        """
        return (
            Otter.objects
            .select_related("species", "rescue")
            .order_by("otter_id")
        )

    def get_context_data(self, **kwargs):
        """
        Adds active_page so the sidebar can highlight the current section.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        return ctx


class OtterCreateView(LoginRequiredMixin, CreateView):
    """
    Creates a new otter record.
    """
    model = Otter
    template_name = "otters/otter_form.html"

    # Fields shown in the form (kept explicit for clarity and control)
    fields = ["name", "date_of_birth", "gender", "weight_kg", "status", "arrival_date", "species", "rescue"]

    # After creating, return to the list page
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "create"
        return ctx


class OtterUpdateView(LoginRequiredMixin, UpdateView):
    """
    Updates an existing otter record.
    """
    model = Otter
    template_name = "otters/otter_form.html"

    # Same fields as create, since you can edit any of these values
    fields = ["name", "date_of_birth", "gender", "weight_kg", "status", "arrival_date", "species", "rescue"]

    # After editing, return to the list page
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "edit"
        return ctx


class OtterDeleteView(LoginRequiredMixin, DeleteView):
    """
    Permanently deletes an otter ONLY if status is 'Released'.
    """
    model = Otter
    template_name = "otters/otter_confirm_delete.html"
    success_url = reverse_lazy("otter_list")

    def post(self, request, *args, **kwargs):
        """
        Override the default POST handler to:
        1) Block deletion unless Released
        2) Catch FK constraint errors
        """
        # Fetch the object to delete
        self.object = self.get_object()

        # Business rule: only released otters can be deleted
        if self.object.status != "Released":
            messages.error(
                request,
                "Only otters with status 'Released' can be permanently deleted."
            )
            return redirect("otter_list")

        try:
            # Attempt the actual delete
            return super().post(request, *args, **kwargs)

        except IntegrityError:
            # MySQL blocked the delete due to related records (FK constraints)
            messages.error(
                request,
                "This otter cannot be deleted because related records exist "
                "(e.g., health assessments)."
            )
            return redirect("otter_list")