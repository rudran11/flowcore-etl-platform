# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""DSL Parser for FlowCore pipelines."""

import hashlib
from typing import Dict, Any, List, Tuple
from pydantic import ValidationError
from flowcore_shared.schemas.pipeline.pipeline import Pipeline
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep
from flowcore_shared.exceptions.parsing import DSLParseError

class DSLParser:
    """
    Parses unvalidated Python dictionaries (usually loaded from YAML/JSON)
    into validated FlowCore metadata schemas, providing rich error context.
    """
    
    SUPPORTED_VERSIONS = ["1.0"]

    @classmethod
    def parse_pipeline_dsl(cls, data: Dict[str, Any]) -> Tuple[Pipeline, List[ExecutionStep]]:
        """
        Parses a complete DSL definition into a Pipeline and its ExecutionSteps.
        """
        if not isinstance(data, dict):
            raise DSLParseError("DSL root must be a dictionary object.")

        # 1. Extensible Versioning
        version = data.get("version", "1.0")
        if version not in cls.SUPPORTED_VERSIONS:
            raise DSLParseError(f"Unsupported DSL version: '{version}'. Supported versions are: {cls.SUPPORTED_VERSIONS}")

        # 2. Pipeline Metadata Mapping
        pipeline_data = data.get("pipeline")
        if not pipeline_data:
            raise DSLParseError("Missing required top-level key: 'pipeline'.")
            
        if not isinstance(pipeline_data, dict):
            raise DSLParseError("'pipeline' must be a dictionary.")

        # Auto-generate ID if absent (simulating backend ID resolution for standalone YAMLs)
        if "id" not in pipeline_data:
            name_seed = pipeline_data.get("name", "unknown")
            pipeline_data["id"] = hashlib.md5(name_seed.encode("utf-8")).hexdigest()

        try:
            pipeline = Pipeline(**pipeline_data)
        except ValidationError as e:
            # Rich error translation
            errors = []
            for err in e.errors():
                loc = ".".join(map(str, err["loc"]))
                errors.append(f"'{loc}': {err['msg']}")
            raise DSLParseError(f"Pipeline validation failed: {'; '.join(errors)}")

        # 3. Execution Steps Mapping
        steps_data = data.get("steps", [])
        if not isinstance(steps_data, list):
            raise DSLParseError("'steps' must be a list of execution step definitions.")
            
        steps = []
        for idx, step_dict in enumerate(steps_data):
            if not isinstance(step_dict, dict):
                raise DSLParseError(f"Step at index {idx} must be a dictionary.")
                
            try:
                steps.append(ExecutionStep(**step_dict))
            except ValidationError as e:
                errors = []
                for err in e.errors():
                    loc = ".".join(map(str, err["loc"]))
                    errors.append(f"'{loc}': {err['msg']}")
                step_identifier = step_dict.get("step_id", f"index[{idx}]")
                raise DSLParseError(f"Step '{step_identifier}' validation failed: {'; '.join(errors)}")

        return pipeline, steps
