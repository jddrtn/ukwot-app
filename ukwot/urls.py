from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    path("otters/", views.OtterListView.as_view(), name="otter_list"),
    path("otters/new/", views.OtterCreateView.as_view(), name="otter_create"),
    path("otters/<int:pk>/edit/", views.OtterUpdateView.as_view(), name="otter_edit"),
    path("otters/<int:pk>/delete/", views.OtterDeleteView.as_view(), name="otter_delete"),
]