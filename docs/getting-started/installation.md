# Installing the CLI

## Installation methods

Choose one of the following installation methods based on your preferences and
environment.

### uv

!!! info "Prerequisites"

    - `git` 2.27+ exists on your `$PATH`

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) 0.6.15+
   (released 2025-04-21) if you haven't already.
1. Install the platform CLI:

    ```sh
    uv tool install git+https://github.com/navapbc/platform-cli
    ```

1. Done. Can now use `nava-platform` directly as in the docs.

For one-off executions:

```sh
uvx --from git+https://github.com/navapbc/platform-cli -- <platform_cli_args>
```

??? note "Management commands"

    Updating:

    ```sh
    uv tool upgrade nava-platform-cli
    ```

    Uninstalling:

    ```sh
    uv tool uninstall nava-platform-cli
    ```

### Nix

!!! info "Prerequisites"

    None! Nix provides everything needed.

1. [Install Nix](https://nixos.org/download/) if you haven't already.
1. Install the platform CLI:

    ```sh
    nix profile add github:navapbc/platform-cli
    ```

1. Done. Can now use `nava-platform` directly as in the docs.

For one-off executions:

```sh
nix run github:navapbc/platform-cli -- <platform_cli_args>
```

??? note "Management commands"

    Updating:

    ```sh
    nix profile upgrade platform-cli
    ```

    Uninstalling:

    ```sh
    nix profile remove platform-cli
    ```

### pipx

!!! info "Prerequisites"

    - `git` 2.27+ exists on your `$PATH`
    - Python 3.11+ available on your system

1. [Install pipx](https://pipx.pypa.io/stable/) if you haven't already
    - Note, pipx requires Python 3.10+ to run itself, but installed tools are
      isolated from system Python packages.
1. Install the platform CLI:

    ```sh
    pipx install git+https://github.com/navapbc/platform-cli
    ```

    **Don't have Python 3.11+?** Let pipx fetch it for you:

    ```sh
    pipx install --fetch-missing-python --python 3.12 git+https://github.com/navapbc/platform-cli
    ```

1. Done. Can now use `nava-platform` directly as in the docs.

For one-off executions:

```sh
pipx run --spec git+https://github.com/navapbc/platform-cli nava-platform <platform_cli_args>
```

??? note "Management commands"

    Updating:

    ```sh
    pipx upgrade nava-platform-cli
    ```

    Uninstalling:

    ```sh
    pipx uninstall nava-platform-cli
    ```

### Container

!!! info "Prerequisites"

    - Docker (or another container runtime)

Container images are not currently published, so you'll need to build it
yourself.

1. Clone the repository
1. Build the container image:

    ```sh
    make build
    ```

1. Instead of using a `nava-platform` command directly, use the wrapper script
   for simplified execution:

    ```sh
    ./bin/container-wrapper infra install ./my_project_directory
    ```

    (or create an alias in your shell like `alias nava-platform =
    <path_to_checkout>/bin/container-wrapper`)

!!! warning

    The `container-wrapper` script makes assumptions about your
    environment. Review the script comments before use.

??? note "Running manually"

    After building, you will have a `nava-platform-cli` image locally available that
    you can run like:

    ```sh
    docker run --rm -it nava-platform-cli
    ```

    For pretty much anything useful, you will need to mount the relevant locations
    from your host system into the container. For example if running the tool in the
    directory of your target project:

    ```sh
    docker run --rm -it -v "$(pwd):/project-dir" nava-platform-cli infra install /project-dir
    ```

## Shell autocompletion

Enable tab completion for your shell:

```sh
nava-platform --install-completion
```

To manually configure completion, get the configuration output:

```sh
nava-platform --show-completion
```
