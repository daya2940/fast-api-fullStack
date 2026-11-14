import uuid
from io import BytesIO

import boto3
from PIL import Image, ImageOps
from starlette.concurrency import run_in_threadpool

from config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.s3_access_key_id.get_secret_value() if settings.s3_access_key_id else None,
        aws_secret_access_key=settings.s3_secret_access_key.get_secret_value() if settings.s3_secret_access_key else None,
        region_name=settings.s3_region_name,
        endpoint_url=settings.s3_endpoint_url,  # Optional custom endpoint URL for S3-compatible services
    )

def process_image(image_file: BytesIO, max_size=(300, 300)) -> tuple[str, BytesIO]:
    image = ImageOps.exif_transpose(Image.open(image_file))

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image = ImageOps.contain(image, max_size, method=Image.Resampling.LANCZOS)

    new_image = Image.new("RGB", max_size, (255, 255, 255))
    new_image.paste(
        image, ((max_size[0] - image.width) // 2, (max_size[1] - image.height) // 2)
    )

    unique_filename = f"{uuid.uuid4().hex}.jpg"
    output_buffer = BytesIO()
    new_image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    return unique_filename, output_buffer

def upload_to_s3(file_buffer: BytesIO, filename: str) -> str:
    get_s3_client().upload_fileobj(
        file_buffer,
        settings.s3_bucket_name,
        filename,
        ExtraArgs={"ContentType": "image/jpeg"},
    )
    return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region_name}.amazonaws.com/{filename}"

def delete_from_s3(filename: str) -> None:
    get_s3_client().delete_object(Bucket=settings.s3_bucket_name, Key=filename)

async def upload_profile_image(file_buffer: BytesIO, filename: str) -> tuple[str, str]:
    key = f"profile-pics/{filename}"
    url = await run_in_threadpool(upload_to_s3, file_buffer, key)
    return key, url

async def delete_profile_image(filename: str | None) -> None:
    if filename is None or filename.strip().lower() in {"", "null", "none"}:
        return
    await run_in_threadpool(delete_from_s3, filename)
