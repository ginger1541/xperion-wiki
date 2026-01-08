"""
Upload API - 이미지 업로드
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import base64
from datetime import datetime
import uuid
import structlog

from app.db.database import get_db
from app.services.github_client import github_client

logger = structlog.get_logger()

router = APIRouter()


class UploadResponse(BaseModel):
    """업로드 응답"""
    url: str
    filename: str
    size: int


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    이미지 업로드 (GitHub 저장)

    - **file**: 이미지 파일 (최대 2MB)

    지원 형식: jpg, jpeg, png, gif, webp
    """

    # 파일 크기 체크 (2MB)
    MAX_SIZE = 2 * 1024 * 1024  # 2MB
    content = await file.read()
    size = len(content)

    if size > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"파일 크기가 너무 큽니다. 최대 2MB까지 업로드 가능합니다. (현재: {size / 1024 / 1024:.2f}MB)"
            }
        )

    # 파일 형식 체크
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": f"지원하지 않는 파일 형식입니다: {file.content_type}"
            }
        )

    try:
        # 고유한 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        new_filename = f"{timestamp}_{unique_id}.{extension}"

        # GitHub에 업로드
        image_path = f"images/{new_filename}"

        github_result = github_client.create_file(
            path=image_path,
            content=base64.b64encode(content).decode('utf-8'),
            message=f"Upload image: {new_filename}",
            is_binary=True
        )

        logger.info("image_uploaded",
                   filename=new_filename,
                   size=size,
                   sha=github_result["sha"])

        # GitHub raw URL 생성
        # 형식: https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
        raw_url = github_result["url"].replace(
            "https://api.github.com/repos/",
            "https://raw.githubusercontent.com/"
        ).replace("/contents/", "/main/")

        return UploadResponse(
            url=raw_url,
            filename=new_filename,
            size=size
        )

    except Exception as e:
        logger.error("image_upload_failed",
                    filename=file.filename,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "code": "UPLOAD_FAILED",
                "message": "이미지 업로드에 실패했습니다."
            }
        )
