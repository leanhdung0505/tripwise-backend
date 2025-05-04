# app/api/routes/email/otp_service.py
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlmodel import Session

from app.crud.users.crud_user import crud_user
from app.services.email.mail_service import (
    create_verification_email,
    create_recovery_email,
    send_email,
)
from app.services.email.otp_token_service import (
    generate_otp,
    create_otp_token,
    verify_otp_token,
)
from app.api.deps import get_session
from app.models import OTPRequest, OTPResponse, OTPResponseData

router = APIRouter(prefix="/otp", tags=["mailservice"])

@router.post("/request", response_model=OTPResponse)
def request_otp(
    *,
    otp_request: OTPRequest,
    session: Session = Depends(get_session),
) -> OTPResponse:
    """
    Send OTP verification code to email.
    - For register: Check if email NOT exists
    - For recovery: Check if email exists
    No authentication required for both cases.
    """
    try:
        # Check email existence based on purpose
        user = crud_user.get_by_email(session=session, email=otp_request.email)
        
        # Generate OTP first
        otp_code = generate_otp()
        
        if otp_request.purpose == "register":
            # For register: Email should NOT exist
            if user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            email_data = create_verification_email(
                email_to=otp_request.email,
                otp_code=otp_code
            )
        else:  # purpose is "recovery"
            # For recovery: Email MUST exist
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Email not found in system"
                )
            email_data = create_recovery_email(
                email_to=otp_request.email,
                otp_code=otp_code,
                full_name=user.full_name
            )

        # Create token
        token = create_otp_token(email=otp_request.email, otp_code=otp_code)

        # Send email using mail service
        send_email(
            email_to=otp_request.email,
            subject=email_data.subject,
            html_content=email_data.html_content
        )

        return OTPResponse(
            data=OTPResponseData(
                message=f"OTP sent to {otp_request.email}",
                token=token
            )
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )


@router.post("/verify", status_code=status.HTTP_200_OK)
def verify_otp(
    token: str = Query(
        ..., 
        description="Token received from /request endpoint"
    ),
    otp_code: str = Query(
        ..., 
        description="5-digit OTP code sent to email",
        min_length=5,
        max_length=5,
        regex="^[0-9]+$"
    )
):
    """
    Verify OTP code sent via email.
    No authentication required - verification is done using the token and OTP code.
    """
    try:
        email = verify_otp_token(token, otp_code)
        return {
            "msg": "Valid OTP",
            "email": email
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP verification: {str(e)}"
        )
