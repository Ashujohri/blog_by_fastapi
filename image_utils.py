from io import BytesIO
from starlette.concurrency import run_in_threadpool
from PIL import Image, ImageOps
from config import settings
import uuid
import boto3


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        aws_access_key_id=(
            settings.S3_ACCESS_KEY_ID.get_secret_value()
            if settings.S3_ACCESS_KEY_ID
            else None
        ),
        aws_secret_access_key=(
            settings.S3_SECRET_ACCESS_KEY.get_secret_value()
            if settings.S3_SECRET_ACCESS_KEY
            else None
        ),
        endpoint_url=settings.S3_ENDPOINT_URL,
    )


def process_profile_image(content: bytes) -> tuple [bytes, str]:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"
        
        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)

    return output.read(), filename

def _upload_to_s3(file_bytes: bytes, key: str) -> None:
    s3 = _get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )

def _delete_from_s3(key: str) -> None:
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)


async def upload_profile_image(file_bytes: bytes, filename: str) -> None:
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_upload_to_s3, file_bytes, key)


async def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_delete_from_s3, key)