# ukwot_app/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from ukwot import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Root URL now redirects to login page
    path("", lambda request: redirect("login")),

    # Authentication routes
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="auth/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Include all routes from the ukwot app
    path("", include("ukwot.urls")),
path("test-after-login/", views.test_after_login, name="test_after_login"),
]