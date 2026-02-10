from django.urls import path
from .views import pull

urlpatterns = [
    path('pull/', pull, name='api_pull'),
]