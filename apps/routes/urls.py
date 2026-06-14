from django.urls import path

from .views import ApiRootView, FuelPlanView


urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("routes/fuel-plan/", FuelPlanView.as_view(), name="fuel-plan"),
]
