from django.urls import path
from .views import LoginView, RegisterView, UserProfileView, ForgotPasswordView, ConfirmPasswordView, ResetPasswordView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('confirm-password/', ConfirmPasswordView.as_view(), name='confirm-password'),
]
