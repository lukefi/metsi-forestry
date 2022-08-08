""" Module contains basic, domain and state spesific utility functions used in preprocessing operations"""
from typing import Optional, Any


# ---- basic utils ----

def get_or_default(maybe: Optional[Any], default: Any = None) -> Any:
    return default if maybe is None else maybe
