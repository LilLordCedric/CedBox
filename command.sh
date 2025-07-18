#!/bin/bash

CWD=$(pwd)
PROJECT_NAME="cedbox"
PROJECT_PYTHON_VERSION="3.12"
ENVIRONMENT_NAME=".venv"

for ARG in "$@"; do
    case "${ARG}" in
        "python")
            echo "Installing Python version..."
            sudo apt install "python${PROJECT_PYTHON_VERSION}" -y

            echo "Installing Python venv package..."
            sudo apt install "python${PROJECT_PYTHON_VERSION}-venv" -y
            ;;

        "package")
            echo "Installing Packages"
            echo "No packages required"
            ;;

        "venv")
            echo "Setting up virtual environment: ${ENVIRONMENT_NAME}"

            if [ -d "${ENVIRONMENT_NAME}" ]; then
                echo "Existing virtual environment found. Deleting..."
                sudo rm -rf "${ENVIRONMENT_NAME}"
            fi

            echo "Creating new virtual environment..."
            python"${PROJECT_PYTHON_VERSION}" -m venv "${ENVIRONMENT_NAME}"

            echo "Activating virtual environment..."
            source "${ENVIRONMENT_NAME}/bin/activate"

            echo "Upgrading pip..."
            pip install --upgrade pip

            echo "Installing dependencies from requirements.txt..."
            pip install -r "requirements.txt"
            ;;

        "build")
            echo "Building distribution packages..."

            echo "Activating virtual environment..."
            source "${ENVIRONMENT_NAME}/bin/activate"

            echo "Cleaning existing dist directory..."
            if [ -d "dist" ]; then
                rm -rf dist
            fi

            echo "Building package..."
            python -m build

            echo "Build completed. Distribution packages are in the dist directory."
            ;;

        "push")
            echo "Pushing distribution packages to PyPI..."

            echo "Activating virtual environment..."
            source "${ENVIRONMENT_NAME}/bin/activate"

            echo "Checking if dist directory exists..."
            if [ ! -d "dist" ]; then
                echo "Error: dist directory not found. Run 'build' command first."
                exit 1
            fi

            echo "Uploading packages to PyPI..."
            python -m twine upload dist/*

            echo "Push completed. Packages have been uploaded to PyPI."
            ;;

        "test")
            echo "Running tests..."

            echo "Activating virtual environment..."
            source "${ENVIRONMENT_NAME}/bin/activate"

            echo "Running pytest..."
            python -m pytest -v tests

            if [ $? -eq 0 ]; then
                echo "All tests passed successfully."
            else
                echo "Some tests failed. Please check the test output for details."
                exit 1
            fi
            ;;

    esac
done
