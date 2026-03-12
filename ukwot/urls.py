from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard_home, name="dashboard_home"),

    # Otter CRUD
    path("otters/", views.OtterListView.as_view(), name="otter_list"),
    path("otters/new/", views.OtterCreateView.as_view(), name="otter_create"),
    path("otters/<int:pk>/edit/", views.OtterUpdateView.as_view(), name="otter_edit"),
    path("otters/<int:pk>/delete/", views.OtterDeleteView.as_view(), name="otter_delete"),

    # Medical Records CRUD
    path("medical-records/", views.MedicalRecordListView.as_view(), name="medical_record_list"),
    path("medical-records/new/", views.MedicalRecordCreateView.as_view(), name="medical_record_create"),
    path("medical-records/<int:pk>/edit/", views.MedicalRecordUpdateView.as_view(), name="medical_record_edit"),
path("medical-records/<int:pk>/delete/", views.MedicalRecordDeleteView.as_view(), name="medical_record_delete"),
]