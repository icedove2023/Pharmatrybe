"""Child-process entrypoint for isolated external plugin execution."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, is_dataclass
from importlib.util import module_from_spec, spec_from_file_location


def main() -> int:
    request = json.loads(sys.stdin.read())
    os.environ.clear()
    os.environ.update(request.get("environment", {}))
    module_path = request["module_path"]
    spec = spec_from_file_location("pharmatrybe_external_worker", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load external plugin module")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    plugin = getattr(module, request["class_name"])()
    plugin.initialize()
    operation = request["operation"]
    payload = request.get("payload")
    context = request.get("context")
    if operation == "predict":
        from app.plugins.base.prediction_plugin import PredictionRequest

        result = plugin.predict(PredictionRequest(payload=payload, context=context))
    elif operation == "search":
        result = plugin.search(payload, context)
    elif operation == "query":
        result = plugin.query(payload)
    elif hasattr(plugin, "execute"):
        result = plugin.execute(payload, context)
    elif hasattr(plugin, "run"):
        result = plugin.run(payload, context)
    else:
        raise TypeError("External plugin does not implement the requested operation")
    if is_dataclass(result):
        result = asdict(result)
    sys.stdout.write(json.dumps({"success": True, "result": result}, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        sys.stdout.write(json.dumps({"success": False, "error": "External plugin execution failed"}))
        raise SystemExit(1)
