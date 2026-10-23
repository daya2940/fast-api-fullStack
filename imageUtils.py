import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

profile_pics_dir = Path("media/profile_pics/")

def process_image(image_file: BytesIO, max_size=(300, 300)) -> str:
    image = ImageOps.exif_transpose(Image.open(image_file))

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image = ImageOps.contain(image, max_size, method=Image.Resampling.LANCZOS)

    new_image = Image.new("RGB", max_size, (255, 255, 255))
    new_image.paste(
        image, ((max_size[0] - image.width) // 2, (max_size[1] - image.height) // 2)
    )

    unique_filename = f"{uuid.uuid4().hex}.jpg"
    save_path = profile_pics_dir / unique_filename

    profile_pics_dir.mkdir(parents=True, exist_ok=True)

    new_image.save(save_path, format="JPEG")

    return unique_filename

def delete_image(image_path: str) -> None:
    if image_path:
        full_path = Path(image_path)
        if full_path.exists():
            full_path.unlink()

