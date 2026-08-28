import importlib

_module = importlib.import_module("packages.prediction-framework.contracts")

for _name in dir(_module):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_module, _name)

__all__ = getattr(_module, "__all__", [])
