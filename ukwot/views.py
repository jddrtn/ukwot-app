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

@login_required
def dashboard_home(request):
    """
    Dashboard landing page.
    Requires login so unauthenticated users are redirected to LOGIN_URL.
    """
    return render(request, "dashboard/home.html", {"active_page": "home"})


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
        - search: q=...
        - sorting: sort=...
        - released-only filter: released=1
        """
        queryset = Otter.objects.select_related("species", "rescue")

        # --- Released-only toggle ---
        # If released=1, we only show Released otters (useful for delete workflow).
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
            "rescue": "rescue__rescue_id",
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