import cloudinary
import cloudinary.uploader

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_file(file, folder: str) -> dict:
    """
    Uploads a file-like object to Cloudinary under the given folder.
    Returns {"url": ..., "public_id": ...} — store both, since public_id
    is needed to delete/replace the file later.
    """
    result = cloudinary.uploader.upload(
        file,
        folder=f"kab-fams/{folder}",
        resource_type="auto",  # handles PDFs and images
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}


def delete_file(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id, resource_type="raw")