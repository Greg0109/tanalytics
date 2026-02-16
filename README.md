# Twitch Analytics API Service

Twitch Analytics API Project to get User and Stream data.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (for environment and dependency management)
- [just](https://github.com/casey/just) (as a command runner)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd tanalytics
    ```

2.  **Create and configure the environment file:**
    Copy the example `.env` file and fill in your Twitch application credentials.
    ```bash
    cp .env.example .env
    ```
    You will need to create an application on the [Twitch Developer Console](https://dev.twitch.tv/console) to get a `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET`.

3.  **Create virtualenv:**
    This command will create a virtual environment using `uv` and install all necessary dependencies.
    ```bash
    just venv
    ```

## Running the Application

To run the FastAPI server locally, use the following command:
```bash
just run
```
The application will be available at `http://127.0.0.1:8000`.

### API Documentation

Once the server is running, interactive API documentation (provided by Swagger UI) is available at `http://127.0.0.1:8000/docs`.

## Available Commands (Justfile)

The `Justfile` provides several commands to streamline development:

-   `just venv`: Creates the virtual environment and installs all dependencies.
-   `just run`: Starts the development server with hot-reloading.
-   `just lint`: Lints the codebase using `ruff`.
-   `just format`: Formats the code using `ruff`.
-   `just typecheck`: Runs static type checking with `mypy`.
-   `just check`: Runs both the linter and the type checker.
-   `just shell`: Activates the virtual environment shell.
