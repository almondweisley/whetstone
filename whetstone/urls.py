"""Top-level URL configuration. The admin is useful for inspecting generated data."""
from django.contrib import admin
from django.urls import path

from exercises import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/runs", views.runs),
    path("api/runs/<int:run_id>", views.run_detail),
    path("api/exercises", views.exercises),
    path("api/discards", views.discards),
]
