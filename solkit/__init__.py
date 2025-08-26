"""Available modules."""

import importlib.util
import sys
from types import ModuleType

from . import common

__all__: list[str] = ['common']


def create_placeholder_module(extra_name: str) -> ModuleType:
    """Create a placeholder module that raises informative errors."""

    class PlaceholderModule(ModuleType):
        def __getattr__(self, attr_name: str) -> None:
            raise ImportError(
                f"The '{extra_name}' module requires the '{extra_name}' extra. "
                f'Install it with: pip install solkit[{extra_name}]'
            )

    return PlaceholderModule(extra_name)


# Conditionally import broker module
if importlib.util.find_spec('aiokafka') is not None:
    from . import broker

    __all__.append('broker')
else:
    broker = create_placeholder_module('broker')
    sys.modules[__name__ + '.broker'] = broker

# Conditionally import cache module
if importlib.util.find_spec('redis') is not None:
    from . import cache

    __all__.append('cache')
else:
    cache = create_placeholder_module('cache')
    sys.modules[__name__ + '.cache'] = cache

# Conditionally import database.sql module
if importlib.util.find_spec('sqlalchemy') is not None:
    from . import database

    __all__.append('database')
else:
    database = create_placeholder_module('database')
    sys.modules[__name__ + '.database'] = create_placeholder_module('database.sql')
