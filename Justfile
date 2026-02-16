default: run

setup:
    @echo "Creating virtual environment with uv..."
    uv venv
    @echo "Installing dependencies..."
    uv pip install -r requirements.txt
    @echo "Setup complete. Activate the virtual environment with 'source .venv/bin/activate'"

install:
    @echo "Installing all dependencies..."
    uv pip install --upgrade pip
    uv pip install -e .[dev]

run:
    @echo "Starting FastAPI server..."
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

lint:
    @echo "Linting code with ruff..."
    ruff check .

format:
    @echo "Formatting code with ruff..."
    uv run ruff format .

typecheck:
    @echo "Type checking with mypy..."
    mypy src

check: lint typecheck

venv:
	uv venv
	uv pip install -e ".[dev]"

shell:
	uv venv
	source .venv/bin/activate
