from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="create"),
    path("register/", views.register, name="create"),
    path("logout/", views.logout, name="create"),
    path("dashboards/", views.dashboards, name="create"),
    path("weekly/", views.report_weekly, name="create"),
    path("daily/", views.report_daily, name="create")
]