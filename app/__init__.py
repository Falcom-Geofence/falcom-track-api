"""Application package for the Falcom Track API.

This package exposes the FastAPI instance via ``app``.  Importing this
module has the side effect of registering all endpoints.
"""

from .main import app  # noqa: F401
