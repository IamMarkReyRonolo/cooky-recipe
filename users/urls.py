# users/urls.py
from django.urls import path
from .views import register_user, obtain_token, list_users, manage_user

urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('token/', obtain_token, name='token-obtain'),
    path('users/', list_users, name='list-users'),
    path('users/<int:user_id>/', manage_user, name='manage-user'),
]
