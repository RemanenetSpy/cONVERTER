"""
Image Converter Module
Handles JPEG, PNG, WebP, and other image format conversions
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim


class ImageConverter:
    """Converts and optimizes images between formats"""

    SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]

    @staticmethod
    def get_format_options(format_str: str, quality: int = 95, progressive: bool = True) -> Dict[str, Any]:
        """Get format-specific save options"""
        
        format_lower = format_str.lower()
        
        if format_lower in ["jpg", "jpeg"]:
            return {
                "quality": min(100, max(1, quality)),
                "optimize": True
            }
        elif format_lower == "png":
            return {
                "optimize": True,
                "compress_level": 9
            }
        elif format_lower == "webp":
            return {
                "quality": min(100, max(1, quality)),
                "method": 6
            }
        elif format_lower == "gif":
            return {
                "optimize": True
            }
        
        return {}

    @staticmethod
    def convert(
        input_path: str,
        output_path: str,
        target_format: str,
        quality: int = 80,
        resize: Optional[Tuple[int, int]] = None,
        grayscale: bool = False,
        normalize: bool = False
    ) -> Dict[str, Any]:
        """Convert image to another format with optional transformations"""
        
        try:
            # Get input format
            input_ext = Path(input_path).suffix.lower()[1:]
            
            # Handle SVG conversion
            if input_ext == 'svg':
                return ImageConverter.svg_to_raster(input_path, output_path, 1024, 1024)
            
            # Handle HEIC conversion
            if input_ext in ['heic', 'heif']:
                return ImageConverter.heic_to_standard(input_path, output_path, quality)
            
            # Standard image conversion
            img = Image.open(input_path)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode != "P" else None)
                img = background
            
            # Apply transformations
            if grayscale:
                img = ImageOps.grayscale(img)
            
            if resize:
                width, height = resize
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            if normalize:
                img = ImageEnhance.Contrast(img).enhance(1.5)
            
            # Save with format options
            save_options = ImageConverter.get_format_options(target_format, quality)
            img.save(output_path, format=target_format.upper(), **save_options)
            
            # Get output metadata
            output_img = Image.open(output_path)
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": f"Converted to {target_format}",
                "outputPath": output_path,
                "format": target_format,
                "dimensions": {
                    "width": output_img.width,
                    "height": output_img.height,
                    "megapixels": round((output_img.width * output_img.height) / 1_000_000, 2)
                },
                "fileSize": output_size
            }
        
        except Exception as e:
            raise Exception(f"Image conversion failed: {str(e)}")

    @staticmethod
    def resize(
        input_path: str,
        output_path: str,
        dimensions: Tuple[int, int],
        preserve_aspect: bool = True
    ) -> Dict[str, Any]:
        """Resize image with aspect ratio preservation"""
        
        try:
            img = Image.open(input_path)
            width, height = dimensions
            
            if preserve_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            img.save(output_path)
            
            return {
                "success": True,
                "message": f"Resized to {img.width}x{img.height}",
                "outputPath": output_path,
                "dimensions": {
                    "width": img.width,
                    "height": img.height
                }
            }
        
        except Exception as e:
            raise Exception(f"Image resize failed: {str(e)}")

    @staticmethod
    def create_thumbnail(
        input_path: str,
        output_path: str,
        size: int = 200,
        quality: int = 80
    ) -> Dict[str, Any]:
        """Create thumbnail from image"""
        
        try:
            img = Image.open(input_path)
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            img.save(output_path, quality=quality, optimize=True)
            
            return {
                "success": True,
                "message": f"Created thumbnail ({size}px)",
                "outputPath": output_path
            }
        
        except Exception as e:
            raise Exception(f"Thumbnail creation failed: {str(e)}")

    @staticmethod
    def get_metadata(image_path: str) -> Dict[str, Any]:
        """Extract image metadata"""
        
        try:
            img = Image.open(image_path)
            file_size = os.path.getsize(image_path)
            
            return {
                "success": True,
                "path": image_path,
                "format": img.format,
                "width": img.width,
                "height": img.height,
                "megapixels": round((img.width * img.height) / 1_000_000, 2),
                "mode": img.mode,
                "fileSize": file_size,
                "fileSizeKB": round(file_size / 1024, 2)
            }
        
        except Exception as e:
            raise Exception(f"Metadata extraction failed: {str(e)}")

    @staticmethod
    def calculate_ssim(image1_path: str, image2_path: str) -> Dict[str, Any]:
        """Calculate Structural Similarity Index between two images"""
        
        try:
            img1 = Image.open(image1_path).convert("L")
            img2 = Image.open(image2_path).convert("L")
            
            # Resize to same dimensions for comparison
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            arr1 = np.array(img1, dtype=np.float64)
            arr2 = np.array(img2, dtype=np.float64)
            
            # Calculate SSIM
            score = ssim(arr1, arr2, data_range=255.0)
            
            return {
                "success": True,
                "score": round(score, 4),
                "quality": "excellent" if score >= 0.95 else 
                          "good" if score >= 0.85 else 
                          "acceptable" if score >= 0.7 else "poor"
            }
        
        except Exception as e:
            raise Exception(f"SSIM calculation failed: {str(e)}")

    @staticmethod
    def batch_convert(
        input_paths: List[str],
        output_dir: str,
        target_format: str,
        quality: int = 80
    ) -> Dict[str, Any]:
        """Convert multiple images at once"""
        
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for input_path in input_paths:
            try:
                basename = Path(input_path).stem
                output_path = os.path.join(output_dir, f"{basename}.{target_format}")
                
                result = ImageConverter.convert(
                    input_path, 
                    output_path, 
                    target_format, 
                    quality
                )
                results.append(result)
            
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "inputPath": input_path
                })
        
        return {
            "success": True,
            "message": f"Batch converted {len(results)} images",
            "total": len(input_paths),
            "successful": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", False)),
            "results": results,
            "outputDir": output_dir
        }

    @staticmethod
    def convert_to_multiple(
        input_path: str,
        output_dir: str,
        formats: List[str],
        quality: int = 80
    ) -> Dict[str, Any]:
        """Convert to multiple formats simultaneously"""
        
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for format_str in formats:
            try:
                basename = Path(input_path).stem
                output_path = os.path.join(output_dir, f"{basename}.{format_str}")
                
                result = ImageConverter.convert(
                    input_path,
                    output_path,
                    format_str,
                    quality
                )
                results.append(result)
            
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "format": format_str
                })
        
        return {
            "success": True,
            "message": f"Converted to {len(formats)} formats",
            "formats": formats,
            "results": results,
            "outputDir": output_dir
        }

    @staticmethod
    def svg_to_raster(
        input_path: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """Convert SVG to PNG or JPEG"""
        
        try:
            import cairosvg
            
            # Determine output format
            output_format = Path(output_path).suffix.lower()[1:]
            
            if output_format == 'png':
                cairosvg.svg2png(
                    url=input_path,
                    write_to=output_path,
                    output_width=width,
                    output_height=height
                )
            elif output_format in ['jpg', 'jpeg']:
                # SVG to PNG first, then to JPEG
                temp_png = output_path.replace('.jpg', '.png').replace('.jpeg', '.png')
                cairosvg.svg2png(
                    url=input_path,
                    write_to=temp_png,
                    output_width=width,
                    output_height=height
                )
                
                # Convert PNG to JPEG
                img = Image.open(temp_png)
                rgb_img = img.convert('RGB')
                rgb_img.save(output_path, 'JPEG', quality=90, optimize=True)
                os.remove(temp_png)
            else:
                raise Exception(f"Unsupported output format: {output_format}")
            
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": f"Converted SVG to {output_format.upper()}",
                "outputPath": output_path,
                "format": output_format,
                "dimensions": {"width": width, "height": height},
                "fileSize": output_size
            }
        
        except ImportError:
            raise Exception("cairosvg library not installed. Install with: pip install cairosvg")
        except Exception as e:
            raise Exception(f"SVG conversion failed: {str(e)}")

    @staticmethod
    def heic_to_standard(
        input_path: str,
        output_path: str,
        quality: int = 90
    ) -> Dict[str, Any]:
        """Convert HEIC to JPEG or PNG"""
        
        try:
            from pillow_heif import register_heif_opener
            
            # Register HEIF opener with Pillow
            register_heif_opener()
            
            # Open HEIC file
            img = Image.open(input_path)
            
            # Determine output format
            output_format = Path(output_path).suffix.lower()[1:]
            
            if output_format in ['jpg', 'jpeg']:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode != 'P' else None)
                    img = background
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
            elif output_format == 'png':
                img.save(output_path, 'PNG', optimize=True)
            else:
                raise Exception(f"Unsupported output format: {output_format}")
            
            output_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "message": f"Converted HEIC to {output_format.upper()}",
                "outputPath": output_path,
                "format": output_format,
                "dimensions": {
                    "width": img.width,
                    "height": img.height
                },
                "fileSize": output_size
            }
        
        except ImportError:
            raise Exception("pillow-heif library not installed. Install with: pip install pillow-heif")
        except Exception as e:
            raise Exception(f"HEIC conversion failed: {str(e)}")
