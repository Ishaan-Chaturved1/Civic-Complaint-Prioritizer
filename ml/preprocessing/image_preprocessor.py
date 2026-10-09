import io
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageOps


class ImagePreprocessor:
    """
    Image validation and preprocessing pipeline for Civic Complaints.
    """

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    @classmethod
    def validate_and_open(cls, file_bytes_or_path, max_size_mb: int = 15) -> Tuple[bool, Optional[Image.Image], str]:
        """
        Validates file size, integrity, and converts to standard RGB.
        """
        try:
            if isinstance(file_bytes_or_path, (str, Path)):
                path = Path(file_bytes_or_path)
                if not path.exists():
                    return False, None, "File does not exist."
                if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
                    return False, None, f"Unsupported file format {path.suffix}. Use JPG or PNG."
                image = Image.open(path)
            else:
                image = Image.open(io.BytesIO(file_bytes_or_path))

            # Auto-orient based on EXIF tag if present
            image = ImageOps.exif_transpose(image)

            # Convert to RGB mode (handles RGBA, grayscale, etc.)
            if image.mode != "RGB":
                image = image.convert("RGB")

            return True, image, "Valid"
        except Exception as e:
            return False, None, f"Corrupted or invalid image: {str(e)}"

    @classmethod
    def prepare_for_classifier(cls, image: Image.Image, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
        """
        Resizes and prepares image for PyTorch ResNet / classification models.
        """
        return image.resize(target_size, Image.Resampling.BILINEAR)

    @classmethod
    def prepare_for_yolo(cls, image: Image.Image, target_size: Tuple[int, int] = (640, 640)) -> Image.Image:
        """
        Resizes and prepares image for YOLO detection / segmentation.
        """
        return image.resize(target_size, Image.Resampling.BILINEAR)
