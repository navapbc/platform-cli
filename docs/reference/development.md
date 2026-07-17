# Development

See the repo's
[CONTRIBUTING.md](https://github.com/navapbc/platform-cli/blob/main/CONTRIBUTING.md)
for foundational contribution guidelines.

## Setup Options

### Option 1: Nix (Recommended)

1. [Install Nix](https://nixos.org/download/) if you haven't already
1. Activate development shell

    ```sh
    nix develop
    ```

1. Run Make targets or `uv` as desired

    - No need to run `make deps` to get started, all the Python dependencies are
      included in the development shell automatically. If you add/remove/update
      Python dependencies in `pyproject.toml`, reload the development shell to
      pick up the changes.

Highly recommended to automate environment activation with
[direnv](https://direnv.net/), which after installing direnv itself, is just:

```sh
echo "use flake" > .envrc && direnv allow
```

??? tip "Use nix-direnv"

    For better caching use [nix-direnv](https://github.com/nix-community/nix-direnv)
    (though there are other options, [see the direnv wiki page for
    Nix](https://github.com/direnv/direnv/wiki/Nix)). Which the easiest way for that
    is to simply have your `.envrc` source in the right version with something like:

    ```sh
    if ! has nix_direnv_version || ! nix_direnv_version 3.1.2; then
      source_url "https://raw.githubusercontent.com/nix-community/nix-direnv/3.1.2/direnvrc" "sha256-Di03ad3a0ueGi6CGrfhrQzyGdQIg9APXIPCAMNQgWYM="
    fi

    use flake
    ```

    The exact version and hash is probably out of date, refer to the [upstream docs
    for best
    info](https://github.com/nix-community/nix-direnv?tab=readme-ov-file#installation).

### Option 2: Non-Nix Setup

For basic development and running Python code, this is relatively
straightforward. For a more complete development environment, see the previous
option.

!!! info "Prerequisites"

    - GNU Make (not strictly, but practically)

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) 0.6.15+
   (released 2025-04-21) if you haven't (`make setup-tooling` for convenience).
1. Install Python dependencies:

    ```sh
    make deps
    ```

1. Run the CLI:

    ```sh
    uv run nava-platform
    ```

## Project layout

Most things should have a (hopefully) obvious name matching their purpose, but
for a overview:

```sh
.
├── bin/              # Utility scripts
├── docs/             # Documentation site source
│   ├── assets/       # Non-plain-text content for the site
│   ├── stylesheets/  # Extra CSS for the site
│   ├── .nav.yaml     # Config file(s) for awesome-nav
│   └── *             # The documentation
├── nava/             # CLI app source code
├── tests/            # Unit tests
├── tests-e2e/        # End-to-end tests for CLI behavior
├── Dockerfile        # Source for the container build of the CLI
├── flake.lock        # Nix
├── flake.nix         # Nix
├── Makefile          # Main development interface
├── mkdocs.yml        # Documentation site config
├── pyproject.toml    # Python stuff config
├── .python-version   # The recommended Python version (for development and end-users)
├── README.md         # This also serves as the home page for the documentation site
└── uv.lock           # Exact versions of Python dependencies
```

## Development Workflow

This is a (fairly) standard Python project using uv for dependency management.

The Makefile has a number of useful commands for development, see the output of
`make help` for a complete list, but common ones you should be using:

```sh
make check         # Run _all_ checks (bascially everything that follows)
make check-static  # Run just static code checks (e.g., formatting and linting)
make fmt[-*]       # Run just the formatting tools (or ones for a specific language), auto-fixing issues
make lint[-*]      # Run just the linting tools (or specific ones)
make test          # Run unit tests
make test-watch    # Run unit tests continually and watch for changes
make test-e2e      # Run "e2e" tests against an installed copy of the tool
```

In general, always run `make check` before pushing up work (configure a
pre-commit hook if you like). This will run effectively all the (basic) code
checks that CI will, but without having to wait on CI.

If your editor can't use the formatting and linting tools to apply fixes as you
edit, you can run the more focused `fmt`/`lint` targets as you go (or fix
everything at the end, your preference).

Run `make test` frequently, or use `make test-watch`. You can adjust behavior
for either with their supported command line arguments via the `args` variable
to the target. For example, to run a single test:

```sh
make test args=tests/util/collections/test_dict.py::test_least_recently_used_dict
```
