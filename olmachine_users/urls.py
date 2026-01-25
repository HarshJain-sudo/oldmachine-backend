"""
URL configuration for olmachine_users app.
"""

from django.urls import path
from olmachine_users.views import LoginOrSignUpView, VerifyOTPView

app_name = 'olmachine_users'

urlpatterns = [
    path(
        'login_or_sign_up/v1/',
        LoginOrSignUpView.as_view(),
        name='login_or_sign_up'
    ),
    path(
        'verify_otp/v1/',
        VerifyOTPView.as_view(),
        name='verify_otp'
    ),
]

