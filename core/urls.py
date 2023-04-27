from django.urls import path

from core.views import UserCreateView, LoginView, ProfileView, PasswordUpdateView

urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', LoginView.as_view()),
    path('profile', ProfileView.as_view()),
    path('update_password', PasswordUpdateView.as_view()),
]
