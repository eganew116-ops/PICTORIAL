from django.contrib import admin
from django.urls import include, path

from operations import views as operations_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("up/", operations_views.healthcheck, name="healthcheck"),
    path("", include("operations.urls")),
]
