# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Configuration loaders for JSON and YAML."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union, List
from flowcore_shared.exceptions.configuration import ConfigurationError

def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Loads and parses a JSON file into a dictionary."""
    path = Path(file_path)
    if not path.is_file():
        raise ConfigurationError(f"JSON file not found: {path}")
    
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON syntax in {path}: {str(e)}")

def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Loads and parses a YAML file into a dictionary."""
    path = Path(file_path)
    if not path.is_file():
        raise ConfigurationError(f"YAML file not found: {path}")
        
    try:
        with path.open("r", encoding="utf-8") as f:
            result = yaml.safe_load(f)
            return result if result is not None else {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML syntax in {path}: {str(e)}")

def load_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Detects file type by extension and delegates to the appropriate loader.
    Supports .json, .yaml, and .yml.
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext == ".json":
        return load_json(path)
    elif ext in (".yaml", ".yml"):
        return load_yaml(path)
    else:
        raise ConfigurationError(f"Unsupported file extension for configuration: {ext}")

def discover_files(directory: Union[str, Path], extensions: List[str] = None) -> List[Path]:
    """
    Recursively discovers configuration files in the specified directory.
    """
    if extensions is None:
        extensions = [".yaml", ".yml", ".json"]
        
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ConfigurationError(f"Directory not found: {dir_path}")
        
    found_files = []
    for ext in extensions:
        found_files.extend(dir_path.rglob(f"*{ext}"))
        
    return sorted(found_files)
