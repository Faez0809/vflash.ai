import os
import platform
import sys


def apply_runtime_compatibility_fixes():
    """Patch Python 3.14 Windows platform detection before SQLAlchemy imports."""
    if sys.platform.startswith("win") and sys.version_info >= (3, 14):
        machine_name = (
            os.environ.get("PROCESSOR_ARCHITEW6432")
            or os.environ.get("PROCESSOR_ARCHITECTURE")
            or "AMD64"
        )

        def _fast_machine():
            return machine_name

        platform.machine = _fast_machine


apply_runtime_compatibility_fixes()
