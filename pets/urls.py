from django.urls import path
from .views import PetViews, PetDetailView


urlpatterns = [
    path("pets/", PetViews.as_view()),
    path("pets/<int:pet_id>/", PetDetailView.as_view()),
]
