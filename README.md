# Nava PBC Platform CLI

Tooling to make installing, upgrading, and using the Nava Platform easier.

## Installation

There are a few ways to get the tool as an end user.

### pipx

[Install pipx](https://pipx.pypa.io/stable/) if you haven't. This requires you
have a working Python installation of some kind just so pipx can run itself.
Things installed via pipx will not depend on the system Python.

Be sure `git` exists on your `$PATH`.

Then install the tool with:

```sh
pipx install git+ssh://git@github.com/navapbc/platform-cli
```

You can now run `nava-platform`.

If you want to get rid of it:

```sh
pipx uninstall nava-platform-cli
```

If it's just a one-off operation and you don't want to install the tool to your
`$PATH`, can use:

```sh
pipx run --spec git+ssh://git@github.com/navapbc/platform-cli nava-platform <platform_cli_args>
```

### Nix

[Install nix](https://nixos.org/download/) if you haven't. This approach
requires nothing else in your environment.

Note, the first time running via nix might take a while building things (as
there's no project shared cache setup currently)! But subsequent runs will be
faster.

You can install the tool with:

```sh
nix profile install --accept-flake-config 'git+ssh://git@github.com/navapbc/platform-cli'
```

Or for one-off runs:

```sh
nix run git+ssh://git@github.com/navapbc/platform-cli -- <platform_cli_args>
```

You can also run particular branches or version of the tooling with this if
needed:

```sh
nix run git+ssh://git@github.com/navapbc/platform-cli?ref=my-branch-for-testing-new-thing-before-its-released -- <platform_cli_args>
```

Alternatively, you can checkout the project locally and in the repository run:

```sh
nix run -- <platform_cli_args>
```

### Docker/Containers

Install Docker if you haven't already. Note, Docker is the default for these
instructions, but other container runtimes may be similar.

Docker images are not currently published, but eventually may be for releases.

To get a Docker image, clone the repository and run:

```sh
make build
```

You will now have a `nava-platform-cli` image locally available that you can run
like:

```sh
docker run --rm -it nava-platform-cli
```

For pretty much anything useful, you will need to mount the relevant locations
from your host system into the container. For example:

```sh
docker run --rm -it -v "$(pwd):/project-dir" nava-platform-cli infra install /project-dir
```

(you may want to define some aliases in your shell for commons invocations like
this)

`bin/docker-wrapper` can automate some of this volume mounting, but also can be
a little fragile, so treat gently.

## Getting Started

After you have `nava-platform` installed, try

```sh
nava-platform infra install --template-uri <path_to_local_copy_of>/template-infra ./just-a-test
```

to see it in action. Then read the docs for how to apply it to existing projects
and more.

## Development

### Setup

For hacking on the tool itself, there are a couple setup options.

#### Standard

[Install poetry](https://python-poetry.org/docs/) >= 1.2.0 if you haven't. The
project is not super sensitive to poetry versions, but try to match the version
listed at the top of `poetry.lock`.

Run `make deps`

Then you can run `poetry run nava-platform`

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

### Process

The project is a standard Python project using poetry for dependency management.

The Makefile has a number of useful commands, see the output of `make help`.

You may want to consider setting up a pre-commit hook for or just manually
running `make check` before pushing work, as this will run useful checks.
