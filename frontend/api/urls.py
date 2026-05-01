from django.urls import path

from .views import pull, search_programs, test_api, universities_list

urlpatterns = [
    path("test/", test_api, name="api_test"),
    path("universities/", universities_list, name="api_universities"),
    path("search/", search_programs, name="api_search"),
    path("pull/", pull, name="api_pull"),
]
