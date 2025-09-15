# This script installs UV and updates the shell configuration file.
# It also initializes current project and syncs the dependencies.

export SHELL_RC=$(echo "$HOME/.${SHELL##*/}rc")
echo $SHELL_RC

if ! command -v uv &>/dev/null; then
  if ! command -v curl &>/dev/null; then
    echo "Error: Need to have curl to install uv"
    exit 1
  else
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
    echo "uv installed."
    echo "testing uv"
    uv --version || exit 1
  fi
else
  echo "uv is already installed."
fi
# Correct python version
uv python install
uv sync
uv run pre-commit install --hook-type commit-msg --hook-type pre-commit

echo "Done"
