from django.urls import path

from .views import (
    OpsLoginView,
    OpsLogoutView,
    dashboard,
    home,
    job_create,
    job_delete,
    job_edit,
    job_export_csv,
    job_list,
    pricing_create,
    pricing_edit,
    pricing_list,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", OpsLoginView.as_view(), name="login"),
    path("logout/", OpsLogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("jobs/<str:machine_type>/", job_list, name="job_list"),
    path("jobs/<str:machine_type>/export/", job_export_csv, name="job_export_csv"),
    path("jobs/<str:machine_type>/new/", job_create, name="job_create"),
    path("jobs/<int:pk>/edit/", job_edit, name="job_edit"),
    path("jobs/<int:pk>/delete/", job_delete, name="job_delete"),
    path("pricing/", pricing_list, name="pricing_list"),
    path("pricing/new/", pricing_create, name="pricing_create"),
    path("pricing/<int:pk>/edit/", pricing_edit, name="pricing_edit"),
]
