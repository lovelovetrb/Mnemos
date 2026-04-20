lint:
	uv run ruff check .
	uv run ruff format .
	uv run minport check .
	uv run pyrefly check .
