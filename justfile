script := "write_logitech_g600_profiles.py"

# List available recipes
default:
    @just --list

# Format the code with ruff
format:
    uv run ruff format {{script}}

# Check formatting without modifying files
format-check:
    uv run ruff format --check {{script}}

# Lint the code with ruff
lint:
    uv run ruff check {{script}}

# Lint and auto-fix what ruff can fix
lint-fix:
    uv run ruff check --fix {{script}}

# Format check + lint (CI-friendly)
check: format-check lint

# Run the script (needs sudo: HID feature reports require root on macOS).
# Pass extra flags through, e.g. `just run --profiles 0 --reuse_connection true`
run *ARGS:
    sudo uv run {{script}} {{ARGS}}
