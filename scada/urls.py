from django.urls import path
from . import views

app_name = "scada"

urlpatterns = [
    path("data/", views.DataView.as_view(), name="data-view"),
    path(
        "inverter/<str:devName>/",
        views.InverterDetailView.as_view(),
        name="inverter-view",
    ),
    path("plant/<str:uid>/", views.PlantDataView.as_view(), name="plant-view"),
]
