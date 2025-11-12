from pathlib import Path
from uuid import uuid4
from PIL import Image
import io
from fastapi import HTTPException, UploadFile, status
from app.config.settings import settings
import boto3


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    endpoint_url=settings.aws_endpoint_url,
    region_name=settings.aws_region,
)


async def validate_image_file(file: UploadFile) -> dict:
    """이미지 파일의 실제 확장자를 검증(리턴)하는 함수"""

    contents = await file.read()

    if len(contents) > settings.image_max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="파일이 너무 큽니다."
        )

    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()

        real_format = image.format.lower()
        if real_format not in ["jpeg", "png", "webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 이미지 형식입니다.",
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 이미지 파일"
        )

    await file.seek(0)
    return {"real_format": real_format, "contents": contents, "filename": file.filename}


def generate_unique_filename(real_format: str) -> str:
    """스토리지에 저장할 랜덤 파일 이름 생성 함수"""

    return f"{uuid4()}.{real_format.lower()}"


async def upload_to_image(file: dict) -> dict:
    """스토리지의 이미지 폴더에 저장하는 함수"""
    
    real_format = file.get('real_format')
    unique_filename = generate_unique_filename(real_format)
    temp_key = f"{settings.image}/{unique_filename}"

    s3_client.upload_fileobj(
        io.BytesIO(file["contents"]),
        settings.aws_bucket_name,
        temp_key,
        ExtraArgs={"ContentType": f"image/{real_format}"},
    )

    return {"unique_filename": unique_filename, "temp_key": temp_key}




async def delete_from_storage(key: str):
    """스토리지에서 파일을 삭제하는 함수"""

    s3_client.delete_object(Bucket=settings.aws_bucket_name, Key=key)


async def generate_presigned_url(
    key: str, expiration: int = settings.url_expire_minute
) -> str:
    """임시 url을 생성하는 함수"""

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.aws_bucket_name, "Key": key},
        ExpiresIn=expiration,
    )

    return url
