lint:
	uv run ruff check . --fix
	uv run ruff format .
	uv run minport check . --fix
	uv run pyrefly check .

test:
	uv run pytest -v
