"""PKM application package.

The app is historically runnable as ``python pkm_app/main.py`` and uses
top-level imports such as ``core.config``. These aliases keep that runtime
shape working while also allowing package imports like
``import pkm_app.services.resource_service`` in tests and tools.
"""

from importlib import import_module
import sys

for _package_name in ("core", "models", "repositories", "services", "ui", "utils"):
    if _package_name not in sys.modules:
        sys.modules[_package_name] = import_module(f"{__name__}.{_package_name}")

for _module_name, _module in list(sys.modules.items()):
    for _package_name in ("core", "models", "repositories", "services", "ui", "utils"):
        if _module_name.startswith(f"{_package_name}."):
            sys.modules.setdefault(f"{__name__}.{_module_name}", _module)
