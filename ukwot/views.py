from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Otter
from .forms import OtterForm
from django.db import models

# ukwot/views.py

@login_required
def dashboard_home(request):
    """
    Dashboard landing page.

    Provides:
    - total otter count
    - released otter count
    - recently added otters
    """
    # Count all otter records in the system
    total_otter_count = Otter.objects.count()

    # Count otters whose status is marked as Released
    released_otter_count = Otter.objects.filter(status="Released").count()

    # Get the 5 most recently added otters based on otter_id
    # (Using otter_id here because it is auto-incrementing and works as a simple
    # "most recently created" indicator in this app.)
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
    model = Otter
    template_name = "otters/otter_list.html"
    context_object_name = "otters"

    """
    Otter list with search/sort/filter + pagination.
    """
    model = Otter
    template_name = "otters/otter_list.html"
    context_object_name = "otters"

    # Paginate results (adjust the number to taste)
    paginate_by = 10
    def get_queryset(self):
        """
        Returns otters with optional:
        - search
        - sorting
        - released-only filter
        """
        queryset = Otter.objects.select_related("species", "rescue")

        # --- Released-only toggle ---
        # If released=1, we only show Released otters
        released_only = (self.request.GET.get("released") == "1")
        if released_only:
            queryset = queryset.filter(status="Released")

        # --- Search ---
        q = (self.request.GET.get("q") or "").strip()
        if q:
            queryset = queryset.filter(
                models.Q(name__icontains=q) |
                models.Q(species__common_name__icontains=q)
            )

        # --- Sorting ---
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
        Pass current query params to template so UI can preserve filters and state.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"

        # Keep the current search/sort/filter values so links can preserve them
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["sort"] = self.request.GET.get("sort", "otter_id")
        ctx["released_only"] = (self.request.GET.get("released") == "1")

        return ctx


class OtterCreateView(LoginRequiredMixin, CreateView):
    """
    Creates a new otter record using OtterForm (dropdowns + date validation).
    """
    model = Otter
    template_name = "otters/otter_form.html"
    form_class = OtterForm  # <-- use the custom form
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        """
        Adds context for sidebar highlighting and create/edit title switching.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["active_page"] = "otters"
        ctx["mode"] = "create"
        return ctx


class OtterUpdateView(LoginRequiredMixin, UpdateView):
    """
    Updates an existing otter record using OtterForm (dropdowns + date validation).
    """
    model = Otter
    template_name = "otters/otter_form.html"
    form_class = OtterForm  # <-- use the custom form
    success_url = reverse_lazy("otter_list")

    def get_context_data(self, **kwargs):
        """
        Adds context for sidebar highlighting and create/edit title switching.
        """
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
        Override the default POST handler to block deletion unless Released
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