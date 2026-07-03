"""
Image conversion via Pillow. This converter is fully functional and
covers the raster formats in the spec (PNG/JPG/JPEG/WEBP/GIF/BMP/TIFF/ICO).

SVG is handled separately: Pillow cannot rasterize SVG (it's not a raster
format), so SVG->raster uses cairosvg if installed, and raster->SVG isn't
a meaningful lossless operation, so it's intentionally not offered.
"""
import io
import mimetypes
from typing import Optional

from PIL import Image

from app.converters.base import BaseConverter, ConversionError, ConversionResult

RASTER_FORMATS = {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico"}

PIL_FORMAT_NAME = {
    "png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "webp": "WEBP",
    "gif": "GIF", "bmp": "BMP", "tiff": "TIFF", "ico": "ICO",
}


class ImageConverter(BaseConverter):
    category = "image"
    supported_conversions = {ext: RASTER_FORMATS - {ext} for ext in RASTER_FORMATS}
    # SVG can be a source (rasterize) but not a target here.
    supported_conversions["svg"] = RASTER_FORMATS

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        options = options or {}
        try:
            if source_ext == "svg":
                image = self._rasterize_svg(data)
            else:
                image = Image.open(io.BytesIO(data))
                image.load()
        except Exception as e:
            raise ConversionError(f"Could not read source image: {e}") from e

        pil_format = PIL_FORMAT_NAME.get(target_ext)
        if not pil_format:
            raise ConversionError(f"Unsupported image target format: {target_ext}")

        # JPEG/BMP/ICO don't support alpha channels — flatten onto white.
        if pil_format in ("JPEG", "BMP") and image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            rgba = image.convert("RGBA")
            background.paste(rgba, mask=rgba.split()[-1])
            image = background
        elif pil_format == "JPEG":
            image = image.convert("RGB")

        buffer = io.BytesIO()
        save_kwargs = {}
        if pil_format == "JPEG":
            save_kwargs["quality"] = options.get("quality", 90)
        if pil_format == "ICO":
            save_kwargs["sizes"] = [(256, 256)]

        image.save(buffer, format=pil_format, **save_kwargs)

        mime_type = mimetypes.guess_type(f"x.{target_ext}")[0] or "application/octet-stream"
        return ConversionResult(
            data=buffer.getvalue(),
            output_extension=target_ext,
            output_mime_type=mime_type,
            metadata={"width": image.width, "height": image.height},
        )

    @staticmethod
    def _rasterize_svg(data: bytes) -> Image.Image:
        try:
            import cairosvg
        except ImportError as e:
            raise ConversionError(
                "SVG rasterization requires the 'cairosvg' package and its "
                "system Cairo dependency to be installed on the server."
            ) from e
        png_bytes = cairosvg.svg2png(bytestring=data)
        return Image.open(io.BytesIO(png_bytes))
