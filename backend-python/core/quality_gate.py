"""
Quality Gate System
Performs integrity checks on conversions
"""

import os
from typing import Dict, Any, Optional
import pandas as pd
from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim


class QualityGate:
    """Quality assurance for file conversions"""

    @staticmethod
    def image_quality_check(
        input_path: str,
        output_path: str,
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """Check image quality using SSIM"""
        
        try:
            img1 = Image.open(input_path).convert("L")
            img2 = Image.open(output_path).convert("L")
            
            # Resize to same dimensions
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            arr1 = np.array(img1, dtype=np.float64)
            arr2 = np.array(img2, dtype=np.float64)
            
            score = ssim(arr1, arr2, data_range=255.0)
            passed = score >= threshold
            
            return {
                "passed": passed,
                "score": round(score, 4),
                "threshold": threshold,
                "quality": "excellent" if score >= 0.95 else 
                          "good" if score >= 0.85 else 
                          "acceptable" if score >= 0.7 else "poor"
            }
        
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "quality": "error"
            }

    @staticmethod
    def csv_excel_quality_check(
        input_path: str,
        output_path: str,
        allow_row_variance: float = 0.05
    ) -> Dict[str, Any]:
        """Check CSV/Excel data integrity"""
        
        try:
            if input_path.endswith(".xlsx") or input_path.endswith(".xls"):
                input_df = pd.read_excel(input_path)
            else:
                input_df = pd.read_csv(input_path)
            
            if output_path.endswith(".xlsx") or output_path.endswith(".xls"):
                output_df = pd.read_excel(output_path)
            else:
                output_df = pd.read_csv(output_path)
            
            input_rows = len(input_df)
            output_rows = len(output_df)
            input_cols = len(input_df.columns)
            output_cols = len(output_df.columns)
            
            row_variance = abs(output_rows - input_rows) / input_rows if input_rows > 0 else 0
            
            passed = row_variance <= allow_row_variance and output_cols == input_cols
            
            return {
                "passed": passed,
                "input": {
                    "rows": input_rows,
                    "columns": input_cols
                },
                "output": {
                    "rows": output_rows,
                    "columns": output_cols
                },
                "variance": {
                    "rows": round(row_variance * 100, 2),
                    "columns": 0 if input_cols == output_cols else "mismatch"
                },
                "quality": "valid" if passed else "invalid"
            }
        
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "quality": "error"
            }

    @staticmethod
    def file_size_check(
        input_path: str,
        output_path: str,
        min_ratio: float = 0.1,
        max_ratio: float = 3.0
    ) -> Dict[str, Any]:
        """Check file size sanity"""
        
        try:
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            ratio = output_size / input_size if input_size > 0 else 0
            
            passed = min_ratio <= ratio <= max_ratio
            
            return {
                "passed": passed,
                "inputSize": input_size,
                "outputSize": output_size,
                "ratio": round(ratio, 2),
                "thresholds": {
                    "minRatio": min_ratio,
                    "maxRatio": max_ratio
                },
                "quality": "valid" if passed else "suspicious"
            }
        
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "quality": "error"
            }

    @staticmethod
    def run_all_checks(
        input_path: str,
        output_path: str,
        conversion_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run all applicable quality checks"""
        
        options = options or {}
        results = {
            "fileSize": QualityGate.file_size_check(input_path, output_path),
            "all_passed": True,
            "checks": []
        }
        
        try:
            # Format-specific checks
            if "image" in conversion_type:
                image_check = QualityGate.image_quality_check(
                    input_path,
                    output_path,
                    options.get("imageQuality", {}).get("threshold", 0.8)
                )
                results["image"] = image_check
                results["checks"].append({"type": "image_ssim", **image_check})
                results["all_passed"] = results["all_passed"] and image_check.get("passed", False)
            
            if "csv" in conversion_type or "excel" in conversion_type:
                csv_check = QualityGate.csv_excel_quality_check(
                    input_path,
                    output_path,
                    options.get("csvExcel", {}).get("allowRowVariance", 0.05)
                )
                results["csv"] = csv_check
                results["checks"].append({"type": "csv_integrity", **csv_check})
                results["all_passed"] = results["all_passed"] and csv_check.get("passed", False)
            
            results["all_passed"] = results["all_passed"] and results["fileSize"].get("passed", False)
            results["checks"].append({"type": "file_size", **results["fileSize"]})
        
        except Exception as e:
            results["error"] = str(e)
            results["all_passed"] = False
        
        return results
