"""
Views for olmachine_users app.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from olmachine_users.serializers import (
    LoginOrSignUpSerializer,
    VerifyOTPSerializer
)
from olmachine_users.models import User
from olmachine_users.services.otp_service import OTPService
from olmachine_users.services.oauth_service import OAuthService
from oldmachine_backend.utils.response_utils import (
    success_response,
    error_response
)

logger = logging.getLogger(__name__)


class LoginOrSignUpView(APIView):
    """
    API view for login or sign up.

    POST /api/marketplace/login_or_sign_up/v1/
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle login or sign up request.

        Args:
            request: HTTP request object

        Returns:
            Response: User ID on success, error on failure
        """
        serializer = LoginOrSignUpSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Invalid phone number or country code",
                res_status="INVALID_PHONE_NUMBER",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        phone_number = serializer.validated_data['phone_number']
        country_code = serializer.validated_data['country_code']

        try:
            with transaction.atomic():
                # Get or create user
                user, created = User.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={'country_code': country_code}
                )

                # Update country code if user exists but code changed
                if not created and user.country_code != country_code:
                    user.country_code = country_code
                    user.save()

                # Create and send OTP
                otp = OTPService.create_otp(user, phone_number)
                otp_sent = OTPService.send_otp(otp)

                if not otp_sent:
                    return error_response(
                        message="Failed to send OTP",
                        res_status="OTP_SEND_FAILED",
                        http_status_code=status.HTTP_400_BAD_REQUEST
                    )

                logger.info(
                    f"Login/SignUp successful for {phone_number}"
                )

                return success_response(
                    data={'user_id': str(user.id)},
                    http_status_code=status.HTTP_200_OK
                )

        except Exception as e:
            logger.error(f"Error in login/signup: {str(e)}")
            return error_response(
                message="An error occurred during login/signup",
                res_status="OTP_SEND_FAILED",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )


class VerifyOTPView(APIView):
    """
    API view for OTP verification.

    POST /api/marketplace/verify_otp/v1/
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle OTP verification request.

        Args:
            request: HTTP request object

        Returns:
            Response: Access and refresh tokens on success
        """
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Invalid phone number or OTP",
                res_status="INVALID_OTP",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp']

        try:
            # Verify OTP
            is_valid, otp = OTPService.verify_otp(phone_number, otp_code)

            if not is_valid or not otp:
                return error_response(
                    message="Invalid or expired OTP",
                    res_status="INVALID_OTP",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )

            # Get user
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return error_response(
                    message="User not found",
                    res_status="INVALID_PHONE_NUMBER",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )

            # Generate OAuth tokens
            tokens = OAuthService.generate_tokens(user)

            logger.info(f"OTP verified successfully for {phone_number}")

            return success_response(
                data=tokens,
                http_status_code=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return error_response(
                message="User not found",
                res_status="INVALID_PHONE_NUMBER",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in OTP verification: {str(e)}")
            return error_response(
                message="OTP verification failed",
                res_status="OTP_VERIFICATION_FAILED",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

