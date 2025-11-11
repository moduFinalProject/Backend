from PIL import Image
import io
from fastapi import HTTPException, UploadFile, status
from app.config.settings import settings

async def validate_image_file(file: UploadFile):
    contents = await file.read()
    
    if len(contents) > settings.image_max_size :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="파일이 너무 큽니다.")
    
    
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
        
        real_format = image.format.lower()
        if real_format not in ['jpeg','png','webp']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="지원하지 않는 이미지 형식입니다.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='유효하지 않은 이미지 파일')
    
    await file.seek(0)
    return {'real_format':real_format, "contents":contents, "filename":file.filename}

