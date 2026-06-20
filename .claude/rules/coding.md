# Coding Rules

Write code as an expert Python Software Engineer would. The following are mandatory:

- **Language:** All code — identifiers, docstrings, comments, log messages, and error strings — MUST be written in **en-US**. No other languages or locales.

- **PEP 8:** Adhere to the official [PEP 8](https://peps.python.org/pep-0008/) Style Guide for structural layout. This includes clear, descriptive `snake_case` names for functions/variables and `PascalCase` for classes. Keep functions focused and small; avoid magic numbers by naming constants.

- **Line length:** Limit all code lines to a maximum of 79 characters to allow side-by-side window reviews.

- **Explicit imports:** Group imports at the top of the file and never use wildcard imports (`from module import *`).

- **Docstrings everywhere:** Every module and every function/method MUST have its own docstring (except `__init__.py` files). Follow the existing Sphinx/reStructuredText style used in the codebase (`:param:`, `:type:`, `:return:`, `:rtype:`) — see `src/imdb/loader.py`.

- **Type hints:** Annotate all function signatures and public attributes with explicit type hints, mirroring the existing use of `typing` (`List`, `Dict`, `Iterator`, etc.).

- **Immutability:** Prefer frozen dataclasses (`@dataclass(frozen=True)`) for data models, as in `src/models/`.

- **Explicit keyword arguments:** Pass arguments by keyword where it improves clarity, consistent with existing calls (e.g., `gzip.open(filename=..., mode=..., encoding=...)`).

- **Comprehensions:** Use list and dictionary comprehensions instead of raw `for` loops for basic collection transformations.

- **Context managers:** Use `with` statements to handle system resources automatically (e.g., opening files or database connections).

- **String formatting:** Prefer f-strings (`f"Hello {name}"`) for clean, highly readable string construction.

- **Data structures:** Use built-in `set` objects to check for uniqueness or existence instead of iterating lists.

- **Linting:** Code MUST pass `pylint src/` cleanly before being considered done.

- **Memory efficiency:** Stream large inputs row-by-row (generators/iterators) instead of loading them into memory, following the pattern in `src/imdb/loader.py`.

- **Async I/O:** Use `async`/`await` with `httpx.AsyncClient` for network calls; bound concurrency with `asyncio.Semaphore` and retry transient failures with `tenacity`, as in `src/clients/tmdb/client.py`.
