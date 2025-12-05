"""
Recipe Manager Module
Handles YAML recipe generation, validation, and storage
"""

import yaml
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class RecipeManager:
    """Manages conversion recipes with checksums and quality tracking"""

    @staticmethod
    def hash_file(file_path: str) -> str:
        """Generate SHA-256 checksum for a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def create_recipe(
        input_file: str,
        output_file: str,
        input_format: str,
        output_format: str,
        parameters: Optional[Dict] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """Create a new conversion recipe"""
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        input_size = os.path.getsize(input_file)
        input_hash = RecipeManager.hash_file(input_file)

        recipe = {
            "version": "1.0",
            "metadata": {
                "created": datetime.utcnow().isoformat() + "Z",
                "userId": user_id,
                "description": f"Convert {input_format} to {output_format}"
            },
            "input": {
                "file": os.path.basename(input_file),
                "format": input_format,
                "size": input_size,
                "hash": input_hash
            },
            "output": {
                "file": os.path.basename(output_file),
                "format": output_format,
                "parameters": parameters or {}
            },
            "quality": {
                "checks": [],
                "passed": True
            },
            "manifest": {
                "checksums": {
                    "input": input_hash,
                    "output": None
                },
                "timeline": [
                    {
                        "step": "initialization",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                ]
            }
        }

        return recipe

    @staticmethod
    def add_quality_check(
        recipe: Dict[str, Any],
        check_name: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add quality check result to recipe"""
        
        recipe["quality"]["checks"].append({
            "name": check_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        if not result.get("passed", True):
            recipe["quality"]["passed"] = False

        return recipe

    @staticmethod
    def finalize_recipe(recipe: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Finalize recipe with output file information"""
        
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Output file not found: {output_file}")
        
        output_size = os.path.getsize(output_file)
        output_hash = RecipeManager.hash_file(output_file)

        recipe["output"]["size"] = output_size
        recipe["manifest"]["checksums"]["output"] = output_hash
        recipe["manifest"]["timeline"].append({
            "step": "completion",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        return recipe

    @staticmethod
    def to_yaml(recipe: Dict[str, Any]) -> str:
        """Convert recipe to YAML string"""
        return yaml.dump(recipe, default_flow_style=False, sort_keys=False)

    @staticmethod
    def save_recipe(recipe: Dict[str, Any], output_path: str) -> str:
        """Save recipe to YAML file"""
        
        recipe_path = output_path.rsplit(".", 1)[0] + ".recipe.yaml"
        yaml_content = RecipeManager.to_yaml(recipe)
        
        with open(recipe_path, "w") as f:
            f.write(yaml_content)
        
        return recipe_path

    @staticmethod
    def load_recipe(recipe_path: str) -> Dict[str, Any]:
        """Load recipe from YAML file"""
        
        if not os.path.exists(recipe_path):
            raise FileNotFoundError(f"Recipe not found: {recipe_path}")
        
        with open(recipe_path, "r") as f:
            recipe = yaml.safe_load(f)
        
        return recipe

    @staticmethod
    def verify_recipe(
        recipe: Dict[str, Any],
        input_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Verify recipe integrity"""
        
        verification = {
            "valid": True,
            "errors": []
        }

        # Check input hash
        if os.path.exists(input_path):
            input_hash = RecipeManager.hash_file(input_path)
            if input_hash != recipe["manifest"]["checksums"]["input"]:
                verification["valid"] = False
                verification["errors"].append("Input file hash mismatch")

        # Check output hash
        if os.path.exists(output_path):
            output_hash = RecipeManager.hash_file(output_path)
            if output_hash != recipe["manifest"]["checksums"]["output"]:
                verification["valid"] = False
                verification["errors"].append("Output file hash mismatch")

        return verification

    @staticmethod
    def add_timeline_event(
        recipe: Dict[str, Any],
        step: str,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add event to recipe timeline"""
        
        event = {
            "step": step,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if details:
            event["details"] = details
        
        recipe["manifest"]["timeline"].append(event)
        return recipe
