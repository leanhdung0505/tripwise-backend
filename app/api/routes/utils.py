from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
# from app.utils import generate_test_email, send_email
import firebase_admin

router = APIRouter(prefix="/utils", tags=["utils"])


# @router.post(
#     "/test-email/",
#     dependencies=[Depends(get_current_active_superuser)],
#     status_code=201,
# )
# def test_email(email_to: EmailStr) -> Message:
#     """
#     Test emails.
#     """
#     email_data = generate_test_email(email_to=email_to)
#     send_email(
#         email_to=email_to,
#         subject=email_data.subject,
#         html_content=email_data.html_content,
#     )
#     return Message(message="Test email sent")

# @router.post("/test-email-nhat", status_code=status.HTTP_201_CREATED)
# def test_email(email_to: EmailStr = Query(..., description="Người nhận email")):
#     try:
#         email_data = generate_test_email(email_to)
#         send_email(
#             email_to=email_to,
#             subject=email_data.subject,
#             html_content=email_data.html_content
#         )
#         return {"msg": f"Email test đã gửi đến {email_to} thành công."}
#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={"msg": "Gửi email thất bại.", "detail": str(e)},
#         )
    

@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.get("/firebase-health/")
async def firebase_health_check() -> dict:
    """
    Kiểm tra Firebase Admin SDK đã được khởi tạo thành công chưa.
    """
    is_initialized = bool(firebase_admin._apps)
    return {"firebase_initialized": is_initialized}


@router.post("/test-fcm/")
async def test_send_fcm_notification(
    token: str = Body(..., embed=True),
):
    """
    Test gửi notification FCM đến 1 device token.
    """
    from firebase_admin import messaging

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="Test Notification",
                body="This is a test FCM notification from TripWise backend."
            ),
            token=token
        )
        response = messaging.send(message)
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}
