"""
Core Conversion Engine
Orchestrates conversions with recipes and quality checks
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .recipe_manager import RecipeManager
from .quality_gate import QualityGate
from .image_converter import ImageConverter
from .document_converter import DocumentConverter


class ConversionEngine:
    """Main conversion orchestrator with recipe and quality tracking"""

    def __init__(
        self,
        output_dir: str = "./output",
        enable_quality_gates: bool = True,
        image_quality_threshold: float = 0.8,
        csv_row_variance: float = 0.05
    ):
        self.output_dir = output_dir
        self.enable_quality_gates = enable_quality_gates
        self.image_quality_threshold = image_quality_threshold
        self.csv_row_variance = csv_row_variance
        
        os.makedirs(output_dir, exist_ok=True)

    def get_format(self, file_path: str) -> str:
        """Get file format from path"""
        return file_path.split(".")[-1].lower()

    def generate_output_path(self, input_path: str, output_format: str) -> str:
        """Generate output file path"""
        basename = Path(input_path).stem
        timestamp = int(datetime.now().timestamp() * 1000)
        return os.path.join(self.output_dir, f"{basename}_{timestamp}.{output_format}")

    def execute_conversion(
        self,
        input_path: str,
        output_path: str,
        conversion_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Execute format-specific conversion"""
        
        options = options or {}
        
        # Image conversions
        if "image" in conversion_type:
            ImageConverter.convert(
                input_path,
                output_path,
                conversion_type.split("_to_")[-1],
                quality=options.get("quality", 80),
                resize=options.get("resize")
            )
        
        # Document conversions
        elif "excel_to_csv" in conversion_type:
            DocumentConverter.excel_to_csv(input_path, output_path)
        elif "csv_to_excel" in conversion_type:
            DocumentConverter.csv_to_excel(input_path, output_path)
        elif "csv_to_parquet" in conversion_type:
            DocumentConverter.csv_to_parquet(input_path, output_path)
        elif "excel_to_parquet" in conversion_type:
            DocumentConverter.excel_to_parquet(input_path, output_path)
        elif "parquet_to_csv" in conversion_type:
            DocumentConverter.parquet_to_csv(input_path, output_path)
        
        else:
            # Default: copy file
            import shutil
            shutil.copy2(input_path, output_path)

    async def convert(
        self,
        input_path: str,
        output_format: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute conversion with recipe and quality checks"""
        
        options = options or {}
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        input_format = self.get_format(input_path)
        output_path = self.generate_output_path(input_path, output_format)
        conversion_type = f"{input_format}_to_{output_format}"
        
        # Create recipe
        recipe = RecipeManager.create_recipe(
            input_path,
            output_path,
            input_format,
            output_format,
            options.get("parameters"),
            options.get("userId", "anonymous")
        )
        
        try:
            # Execute conversion
            RecipeManager.add_timeline_event(recipe, "conversion_started")
            self.execute_conversion(input_path, output_path, conversion_type, options)
            RecipeManager.add_timeline_event(recipe, "conversion_completed")
            
            # Run quality checks
            if self.enable_quality_gates:
                quality_results = QualityGate.run_all_checks(
                    input_path,
                    output_path,
                    conversion_type,
                    {
                        "imageQuality": {"threshold": self.image_quality_threshold},
                        "csvExcel": {"allowRowVariance": self.csv_row_variance}
                    }
                )
                
                recipe["quality"] = quality_results
                RecipeManager.add_timeline_event(recipe, "quality_check_completed")
                
                # Rollback if quality checks fail
                if not quality_results.get("all_passed", True):
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    recipe["quality"]["passed"] = False
                    return {
                        "success": False,
                        "error": "Quality checks failed",
                        "recipe": recipe,
                        "details": quality_results
                    }
            
            # Finalize recipe
            RecipeManager.finalize_recipe(recipe, output_path)
            recipe_path = RecipeManager.save_recipe(recipe, output_path)
            
            return {
                "success": True,
                "outputPath": output_path,
                "recipePath": recipe_path,
                "recipe": recipe,
                "message": f"Conversion successful: {input_format} → {output_format}"
            }
        
        except Exception as e:
            # Clean up on error
            if os.path.exists(output_path):
                os.remove(output_path)
            
            return {
                "success": False,
                "error": str(e),
                "recipe": recipe
            }

    async def batch_convert(
        self,
        file_list: List[str],
        output_format: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Batch convert multiple files"""
        
        options = options or {}
        results = []
        
        for file_path in file_list:
            try:
                result = await self.convert(file_path, output_format, options)
                results.append(result)
            except Exception as e:
                results.append({
                    "file": file_path,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total": len(file_list),
            "successful": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", False)),
            "results": results
        }

    async def rerun_from_recipe(
        self,
        recipe_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Re-run a conversion from a recipe"""
        
        try:
            recipe = RecipeManager.load_recipe(recipe_path)
            
            if not recipe:
                raise ValueError("Invalid recipe file")
            
            input_file = recipe["input"]["file"]
            output_format = recipe["output"]["format"]
            
            return await self.convert(
                input_file,
                output_format,
                {
                    **(options or {}),
                    "parameters": recipe["output"].get("parameters", {})
                }
            )
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
