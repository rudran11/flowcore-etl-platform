import pytest
import json
import yaml
from pathlib import Path
from flowcore.parsing.loaders import load_json, load_yaml, load_file, discover_files
from flowcore_shared.exceptions.configuration import ConfigurationError

def test_load_json_success(tmp_path):
    f = tmp_path / "config.json"
    f.write_text('{"key": "value"}')
    data = load_json(f)
    assert data == {"key": "value"}

def test_load_json_syntax_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text('{"key": "value", }')
    with pytest.raises(ConfigurationError, match="Invalid JSON syntax"):
        load_json(f)

def test_load_yaml_success(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text('key: value\nlist:\n  - 1\n  - 2')
    data = load_yaml(f)
    assert data == {"key": "value", "list": [1, 2]}

def test_load_yaml_empty(tmp_path):
    f = tmp_path / "empty.yaml"
    f.write_text('')
    data = load_yaml(f)
    assert data == {}

def test_load_yaml_syntax_error(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text('key: "value\nmissing_quote: true')
    with pytest.raises(ConfigurationError, match="Invalid YAML syntax"):
        load_yaml(f)

def test_load_file_routing(tmp_path):
    j = tmp_path / "test.json"
    j.write_text('{"a": 1}')
    y = tmp_path / "test.yml"
    y.write_text('b: 2')
    
    assert load_file(j) == {"a": 1}
    assert load_file(y) == {"b": 2}

def test_load_file_unsupported(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text('hello')
    with pytest.raises(ConfigurationError, match="Unsupported file extension"):
        load_file(f)

def test_discover_files(tmp_path):
    (tmp_path / "d1").mkdir()
    (tmp_path / "d1" / "f1.json").write_text("{}")
    (tmp_path / "d1" / "f2.yaml").write_text("")
    (tmp_path / "d1" / "f3.txt").write_text("")
    
    files = discover_files(tmp_path)
    # 2 files matched extensions
    assert len(files) == 2
    exts = [f.suffix for f in files]
    assert ".json" in exts
    assert ".yaml" in exts

def test_file_not_found():
    with pytest.raises(ConfigurationError, match="not found"):
        load_json("does_not_exist.json")
    with pytest.raises(ConfigurationError, match="not found"):
        load_yaml("does_not_exist.yaml")
    with pytest.raises(ConfigurationError, match="Directory not found"):
        discover_files("does_not_exist_dir")
