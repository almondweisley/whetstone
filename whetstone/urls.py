"""Top-level URL configuration. The admin is useful for inspecting generated data."""
from django.contrib import admin
from django.urls import path

urlpatterns = [path("admin/", admin.site.urls)]

