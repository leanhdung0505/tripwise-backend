import cloudinary
import cloudinary.uploader
from app.core.config import settings 

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_image_to_cloudinary(file, folder="user_avatars"):
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        overwrite=True,
        resource_type="image"
    )
    return result.get("secure_url")