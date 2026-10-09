import os
import shutil
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile
from app.config import settings


class StorageService:
    """
    Local file storage service compatible with future S3 migration.
    Stores files under uploads/complaints/{complaint_id}/
    """

    @staticmethod
    def get_complaint_dir(complaint_id: str) -> Path:
        target_dir = settings.UPLOAD_DIR / "complaints" / complaint_id
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    @classmethod
    async def save_uploaded_complaint_image(cls, complaint_id: str, file: UploadFile) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Saves uploaded file to complaint directory and returns (success, relative_url, absolute_path).
        """
        if not file or not file.filename:
            return False, None, None

        ext = Path(file.filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            return False, None, "Unsupported file format. Please upload JPG or PNG."

        comp_dir = cls.get_complaint_dir(complaint_id)
        saved_filename = f"original{ext}"
        destination = comp_dir / saved_filename

        try:
            with open(destination, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            relative_url = f"/uploads/complaints/{complaint_id}/{saved_filename}"
            return True, relative_url, str(destination.resolve())
        except Exception as e:
            return False, None, f"Failed to save image: {str(e)}"

    @classmethod
    def get_annotated_path(cls, complaint_id: str) -> Tuple[str, str]:
        comp_dir = cls.get_complaint_dir(complaint_id)
        annotated_file = comp_dir / "detection.jpg"
        relative_url = f"/uploads/complaints/{complaint_id}/detection.jpg"
        return str(annotated_file.resolve()), relative_url
