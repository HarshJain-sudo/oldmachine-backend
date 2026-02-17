"""
Views for olmachine_users app.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from olmachine_users.serializers import (
    LoginOrSignUpSerializer,
    VerifyOTPSerializer,
    RefreshTokenSerializer,
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

    @swagger_auto_schema(
        operation_summary="Login or Sign Up",
        operation_description=(
            "Initiate login or sign up process by sending phone number. "
            "An OTP will be sent to the provided phone number for verification."
        ),
        request_body=LoginOrSignUpSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                examples={
                    "application/json": {
                        "data": {
                            "user_id": "uuid-string",
                            "message": "OTP sent successfully"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Invalid phone number or country code"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=['Authentication']
    )
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

    @swagger_auto_schema(
        operation_summary="Verify OTP and get access token",
        operation_description=(
            "Verify the OTP code sent to the phone number. "
            "Upon successful verification, returns OAuth2 access token "
            "and refresh token for API authentication."
        ),
        request_body=VerifyOTPSerializer,
        responses={
            200: openapi.Response(
                description="OTP verified successfully",
                examples={
                    "application/json": {
                        "data": {
                            "access_token": "token-string",
                            "refresh_token": "refresh-token-string",
                            "token_type": "Bearer",
                            "expires_in": 86400
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Invalid or expired OTP"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=['Authentication']
    )
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


class RefreshTokenView(APIView):
    """
    API view to exchange a refresh token for a new access token.

    POST /api/marketplace/refresh_token/v1/
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description=(
            "Exchange a valid refresh token (from verify_otp) for a new "
            "access token. Returns the new access_token and the same "
            "refresh_token for future refreshes. No client_id/client_secret."
        ),
        request_body=RefreshTokenSerializer,
        responses={
            200: openapi.Response(
                description="New tokens returned",
                examples={
                    "application/json": {
                        "access_token": "new-token-string",
                        "refresh_token": "refresh-token-string",
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Missing or invalid/expired refresh token"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=['Authentication']
    )
    def post(self, request):
        """
        Handle refresh token request.

        Returns:
            Response: New access_token and refresh_token on success.
        """
        serializer = RefreshTokenSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Refresh token is required",
                res_status="INVALID_REFRESH_TOKEN",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            tokens = OAuthService.refresh_access_token(
                serializer.validated_data['refresh_token']
            )
            return success_response(
                data=tokens,
                http_status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                message=str(e) or "Invalid or expired refresh token",
                res_status="INVALID_REFRESH_TOKEN",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in refresh token: {str(e)}")
            return error_response(
                message="Invalid or expired refresh token",
                res_status="INVALID_REFRESH_TOKEN",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

