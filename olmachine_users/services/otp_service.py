"""
OTP service for generating and sending OTP codes.
"""

import random
import logging
from django.utils import timezone
from django.conf import settings
from olmachine_users.models import OTP, User

logger = logging.getLogger(__name__)


class OTPService:
    """Service for OTP generation and verification."""

    @staticmethod
    def generate_otp_code():
        """
        Generate OTP code.
        
        Currently hardcoded to '000000' (6 digits) for development.
        TODO: Replace with actual OTP generation later.

        Returns:
            str: Generated OTP code
        """
        # Hardcoded OTP for development/testing (6 digits)
        return "000000"
        
        # TODO: Uncomment below for production OTP generation
        # otp_length = getattr(settings, 'OTP_LENGTH', 6)
        # return str(random.randint(
        #     10 ** (otp_length - 1),
        #     10 ** otp_length - 1
        # )).zfill(otp_length)

    @staticmethod
    def create_otp(user, phone_number):
        """
        Create and save OTP for user.

        Args:
            user: User instance
            phone_number: Phone number

        Returns:
            OTP: Created OTP instance
        """
        otp_code = OTPService.generate_otp_code()
        expiry_seconds = getattr(settings, 'OTP_EXPIRY_SECONDS', 300)
        expires_at = timezone.now() + timezone.timedelta(
            seconds=expiry_seconds
        )

        otp = OTP.objects.create(
            user=user,
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )

        logger.info(f"OTP created for {phone_number}")

        return otp

    @staticmethod
    def send_otp(otp):
        """
        Send OTP to user's phone number.

        Args:
            otp: OTP instance

        Returns:
            bool: True if OTP sent successfully
        """
        otp_service_enabled = getattr(
            settings,
            'OTP_SERVICE_ENABLED',
            False
        )

        if not otp_service_enabled:
            # In development/beta, log OTP instead of sending
            logger.info(
                f"OTP for {otp.phone_number}: {otp.otp_code}"
            )
            return True

        # TODO: Integrate with actual SMS service (Twilio, AWS SNS, etc.)
        # For now, just log it
        logger.info(
            f"OTP sent to {otp.phone_number}: {otp.otp_code}"
        )
        return True

    @staticmethod
    def verify_otp(phone_number, otp_code):
        """
        Verify OTP code for phone number.

        Args:
            phone_number: Phone number
            otp_code: OTP code to verify

        Returns:
            tuple: (is_valid, otp_instance) or (False, None)
        """
        try:
            otp = OTP.objects.filter(
                phone_number=phone_number,
                otp_code=otp_code,
                is_verified=False
            ).order_by('-created_at').first()

            if not otp:
                return False, None

            if otp.is_expired():
                logger.warning(
                    f"Expired OTP attempted for {phone_number}"
                )
                return False, None

            if otp.verify():
                logger.info(f"OTP verified for {phone_number}")
                return True, otp

            return False, None

        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}")
            return False, None

