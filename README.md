# Nava PBC Platform CLI

Tooling to make installing, upgrading, and using the Nava Platform easier.

## Installation

There are a few ways to get the tool as an end user.

### uv

> [!IMPORTANT]
> Prereqs:
>
> - `git` 2.27+ exists on your `$PATH`

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) 0.5.8+
(released 2024-12-11) if you haven't.

Then install the tool with:

```sh
uv tool install git+https://github.com/navapbc/platform-cli
```

One-off run:
```sh
uvx --from git+https://github.com/navapbc/platform-cli -- <platform_cli_args>
```

<details>

<summary>Other notes</summary>

```sh
uv tool upgrade nava-platform-cli
```

```sh
uv tool uninstall nava-platform-cli
```

</details>

### pipx

> [!IMPORTANT]
> Prereqs:
>
> - `git` 2.27+ exists on your `$PATH`
> - Python 3.8+ available on your system

[Install pipx](https://pipx.pypa.io/stable/) if you haven't. This does require
you have a working Python 3.8+ installation of some kind so pipx can run itself.
Things installed via pipx will not depend on the system Python packages, though
may re-use the system interpreter.

Then if you have Python 3.11+ available already, install the tool with:

```sh
pipx install git+https://github.com/navapbc/platform-cli
```

<details>

<summary>If you don't have Python 3.11+ available</summary>

You can have pipx fetch and install an appropriate Python version for you, with
the slightly longer:

```sh
pipx install --fetch-missing-python --python 3.12 git+https://github.com/navapbc/platform-cli
```

</details>

You can now run `nava-platform`. See [Getting Started](#getting-started).

If it's just a one-off operation and you don't want to install the tool to your
`$PATH`, can use:

```sh
pipx run --spec git+https://github.com/navapbc/platform-cli nava-platform <platform_cli_args>
```

<details>

<summary>Other notes</summary>

If you want to get rid of it:

```sh
pipx uninstall nava-platform-cli
```

Upgrade with:

```sh
pipx upgrade nava-platform-cli
```

(or uninstall and install again)

</details>

### Nix

[Install nix](https://nixos.org/download/) if you haven't. This approach
requires nothing else in your environment.

Note, the first time running via nix might take a while building things (as
there's no project shared cache setup currently)! But subsequent runs will be
faster.

You can install the tool with:

```sh
nix profile install github:navapbc/platform-cli
```

You can now run `nava-platform`. See [Getting Started](#getting-started).

For one-off runs:

```sh
nix run github:navapbc/platform-cli -- <platform_cli_args>
```

<details>

<summary>Other notes</summary>

Upgrade with:

``` sh
nix profile upgrade platform-cli
```

Uninstall with:

``` sh
nix profile remove platform-cli
```

Alternatively for one-offs, you can checkout the project locally and in the
repository run:

```sh
nix run . -- <platform_cli_args>
```

</details>

### Docker/Container

Install Docker if you haven't already. Note, Docker is the default for these
instructions, but other container runtimes may be similar.

Docker images are not currently published, so you'll need to build it yourself.

To get a Docker image, clone the repository and run:

```sh
make build
```

`bin/docker-wrapper` exists to streamline running via Docker, so you can just:

```sh
./bin/docker-wrapper infra install ./my_project_directory
```

(it can be a little fragile, so treat gently and read about the assumptions it
makes in the comments of the script)

<details>

<summary>Running manually</summary>

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

(you may want to define some aliases in your shell for commons invocations like
this)

</details>

## Getting Started

After you have `nava-platform` installed, if you want to see the tool in action
immediately, try:

```sh
nava-platform infra install ./just-a-test
```

Then read [the docs](./docs/getting-started/index.md) for how to apply it to
existing projects and more.

### Shell Completion

You can install completion support for the CLI by running:

```sh
nava-platform --install-completion
```

Or if you want to put the config in a particular location for your shell
manually, you need the output from:

```sh
nava-platform --show-completion
```

## Development

### Setup

For hacking on the tool itself, there are a couple setup options.

#### Standard

> [!IMPORTANT]
> Prereqs:
>
> - GNU Make (not strictly, but practically)

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) 0.5.8+
(released 2024-12-11) if you haven't (`make setup-tooling` for convenience).

Run `make deps`

Then you can run `uv run nava-platform`

#### Nix

`nix develop` will drop you into a shell with all dev tooling and python
dependencies installed.

You can automate this with direnv.

```sh
echo "use flake" > .envrc && direnv allow
```

But you probably want to use
[nix-direnv](https://github.com/nix-community/nix-direnv) (though there are
other options, [see the direnv wiki page for
Nix](https://github.com/direnv/direnv/wiki/Nix)). Which the easiest way for that
is to simply have your `.envrc` source in the right version with something like:

```sh
if ! has nix_direnv_version || ! nix_direnv_version 3.0.6; then
  source_url "https://raw.githubusercontent.com/nix-community/nix-direnv/3.0.6/direnvrc" "sha256-RYcUJaRMf8oF5LznDrlCXbkOQrywm0HDv1VjYGaJGdM="
fi

use flake
```

The exact version and hash is probably out of date, refer to the [upstream docs
for best
info](https://github.com/nix-community/nix-direnv?tab=readme-ov-file#installation).

You can then use the `uv` command as normal, or run tooling directly.

### Process

The project is a standard Python project using uv for dependency management.

The Makefile has a number of useful commands, see the output of `make help`.

You may want to consider setting up a pre-commit hook for or just manually
running `make check` before pushing work, as this will run useful checks.

# Credits

Icon designed by OpenMoji – the open-source emoji and icon project. License: [CC
BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/#)

Built on the back of [Copier](https://github.com/copier-org/copier).

