<p>
  <img src="docs/assets/Nava-Strata-Logo-V02.svg" alt="Nava Strata" width="400">
</p>
<p><i>Open source tools for every layer of government service delivery.</i></p>
<p><b>Strata is a gold-standard target architecture and suite of open-source tools that gives government agencies everything they need to run a modern service.</b></p>

<h4 align="center">
  <a href="https://github.com/navapbc/platform-cli/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-apache_2.0-red" alt="Nava Strata is released under the Apache 2.0 license" >
  </a>
  <a href="https://github.com/navapbc/platform-cli/blob/main/CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen" alt="PRs welcome!" />
  </a>
  <a href="https://github.com/navapbc/platform-cli/issues">
    <img src="https://img.shields.io/github/commit-activity/m/navapbc/platform-cli" alt="git commit activity" />
  </a>
  <a href="https://github.com/navapbc/platform-cli/repos/">
    <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/navapbc/platform-cli/total">
  </a>
</h4>

# Nava PBC Platform CLI

A command-line tool that simplifies installing, upgrading, and managing Nava Strata.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
  - [uv (Recommended)](#uv)
  - [pipx](#pipx)
  - [Nix](#nix)
  - [Docker/Container](#dockercontainer)
- [Getting Started](#getting-started)
- [Development](#development)
- [Credits](#credits)

---

## Quick Start

Try the tool immediately after installation:

```sh
nava-platform infra install ./just-a-test
```

For detailed usage and integration with existing projects, see [the documentation](./docs/getting-started/index.md).

---

## Installation

Choose one of the following installation methods based on your preferences and environment.

### uv

**Recommended for most users.**

**Prerequisites:**
- `git` 2.27+ on your `$PATH`

**Steps:**

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) 0.5.8+ (released 2024-12-11)

2. Install the platform CLI:
   ```sh
   uv tool install git+https://github.com/navapbc/platform-cli
   ```

**One-off execution** (without installing):
```sh
uvx --from git+https://github.com/navapbc/platform-cli -- <platform_cli_args>
```

**Management commands:**
```sh
# Upgrade
uv tool upgrade nava-platform-cli

# Uninstall
uv tool uninstall nava-platform-cli
```

### pipx

**Good alternative if you already have Python installed.**

**Prerequisites:**
- `git` 2.27+ on your `$PATH`
- Python 3.8+ available on your system

**Steps:**

1. [Install pipx](https://pipx.pypa.io/stable/) if you haven't already

2. Install the platform CLI:
   ```sh
   pipx install git+https://github.com/navapbc/platform-cli
   ```
   
   **Don't have Python 3.11+?** Let pipx fetch it for you:
   ```sh
   pipx install --fetch-missing-python --python 3.12 git+https://github.com/navapbc/platform-cli
   ```

**One-off execution** (without installing):
```sh
pipx run --spec git+https://github.com/navapbc/platform-cli nava-platform <platform_cli_args>
```

**Management commands:**
```sh
# Upgrade
pipx upgrade nava-platform-cli

# Uninstall
pipx uninstall nava-platform-cli
```

> **Note:** pipx requires Python 3.8+ to run itself, but installed tools are isolated from system Python packages.

### Nix

**For users who prefer reproducible builds and declarative environments.**

> [!WARNING]
> Currently broken on macOS due to [upstream issues](https://github.com/copier-org/copier/issues/1595)

**Prerequisites:**
- None! Nix provides everything needed.

**Steps:**

1. [Install Nix](https://nixos.org/download/) if you haven't already

2. Install the platform CLI:
   ```sh
   nix profile install github:navapbc/platform-cli
   ```

**One-off execution** (without installing):
```sh
nix run github:navapbc/platform-cli -- <platform_cli_args>
```

**Management commands:**
```sh
# Upgrade
nix profile upgrade platform-cli

# Uninstall
nix profile remove platform-cli
```

**For local development:**
```sh
# From within the cloned repository
nix run . -- <platform_cli_args>
```

> **Note:** First-time execution may take longer due to building dependencies. Subsequent runs will be faster.

### Docker/Container

**For containerized environments or when you want complete isolation.**

**Prerequisites:**
- Docker (or another container runtime)

**Steps:**

1. Clone the repository

2. Build the Docker image:
   ```sh
   make build
   ```

3. Use the wrapper script for simplified execution:
   ```sh
   ./bin/docker-wrapper infra install ./my_project_directory
   ```

> **Note:** The `docker-wrapper` script makes assumptions about your environment. Review the script comments before use.

**Manual execution:**

After building, run the container directly:
```sh
docker run --rm -it nava-platform-cli
```

**With volume mounting** (required for most operations):
```sh
docker run --rm -it -v "$(pwd):/project-dir" nava-platform-cli infra install /project-dir
```

> **Tip:** Consider creating shell aliases for common invocations.

---

## Getting Started

Once you have `nava-platform` installed, you can start using it immediately.

### Basic Usage

Test the installation with a simple command:

```sh
nava-platform infra install ./just-a-test
```

### Documentation

For comprehensive guides on using the platform CLI with existing projects:
- [Getting Started Guide](./docs/getting-started/index.md)
- [New Project Setup](./docs/getting-started/new-project.md)
- [Migrating from Legacy Template](./docs/getting-started/migrating-from-legacy-template.md)

### Shell Completion

Enable tab completion for your shell:

```sh
nava-platform --install-completion
```

To manually configure completion, get the configuration output:

```sh
nava-platform --show-completion
```

---

## Development

Contributing to the platform CLI? Here's how to set up your development environment.

### Setup Options

#### Option 1: Standard Setup (Recommended)

**Prerequisites:**
- GNU Make

**Steps:**

1. Install uv 0.5.8+ (released 2024-12-11):
   ```sh
   # Or use: make setup-tooling
   ```
   [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)

2. Install dependencies:
   ```sh
   make deps
   ```

3. Run the CLI:
   ```sh
   uv run nava-platform
   ```

#### Option 2: Nix Development Environment

> [!WARNING]
> Currently broken on macOS due to [upstream issues](https://github.com/copier-org/copier/issues/1595)

**Enter the development shell:**
```sh
nix develop
```

**Automate with direnv:**

Basic setup:
```sh
echo "use flake" > .envrc && direnv allow
```

**Recommended:** Use [nix-direnv](https://github.com/nix-community/nix-direnv) for better caching. Add to `.envrc`:
```sh
if ! has nix_direnv_version || ! nix_direnv_version 3.0.6; then
  source_url "https://raw.githubusercontent.com/nix-community/nix-direnv/3.0.6/direnvrc" "sha256-RYcUJaRMf8oF5LznDrlCXbkOQrywm0HDv1VjYGaJGdM="
fi

use flake
```

> **Note:** Check the [nix-direnv docs](https://github.com/nix-community/nix-direnv?tab=readme-ov-file#installation) for the latest version and hash.

### Development Workflow

This is a standard Python project using **uv** for dependency management.

**Useful commands:**
```sh
# See all available commands
make help

# Run quality checks
make check
```

**Best practices:**
- Run `make check` before pushing changes
- Consider setting up a pre-commit hook for automated checks
- See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines

## Credits

**Icon:** Designed by [OpenMoji](https://openmoji.org/) – the open-source emoji and icon project  
License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/#)

**Built with:** [Copier](https://github.com/copier-org/copier) – Template project generator

---

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

## Community

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

