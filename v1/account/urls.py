from django.urls import path
from .views import GetCreateToken,GetUser

urlpatterns = [
    path('login',GetCreateToken.as_view(),name="get_create_account"),
    path("user",GetUser.as_view(),name="get_user")
]