# Nava Platform CLI

_Part of [Nava Strata](https://github.com/navapbc/strata)._

<p align="center">
  <a href="https://github.com/navapbc/platform-cli/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-apache_2.0-red" alt="Nava Strata is released under the Apache 2.0 license" >
  </a>
  <a href="https://github.com/navapbc/platform-cli/blob/main/CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen" alt="PRs welcome!" />
  </a>
  <a href="https://github.com/navapbc/platform-cli/commits/main">
    <img src="https://img.shields.io/github/commit-activity/m/navapbc/platform-cli" alt="git commit activity" />
  </a>
</p>

A command-line tool that simplifies installing, upgrading, and managing Nava Strata.

## Installation

Recommended options:

- uv: `uv tool install git+https://github.com/navapbc/platform-cli`
- Nix: `nix profile add github:navapbc/platform-cli`

> [!TIP]
>
> The CLI can be installed in additional ways which may fit your needs better.
> See all the supported methods in [the installation
> documentation](./docs/getting-started/installation.md).

## Getting started

After you have `nava-platform` installed, you can try out a Strata template
install just to see things working:

```sh
nava-platform infra install ./just-a-test
```

Then refer to [the main Getting started documentation][docs-getting-started] for
how to use it with existing projects and more.

[docs-getting-started]: ./docs/getting-started/index.md

## Documentation

In-depth documentation is available at
<https://navapbc.github.io/platform-cli/>.

When running `nava-platform` itself, use the `--help` flag on commands for more
information.

## Development

Interested in contributing to the project? See [the development
documentation][docs-development].

[docs-development]: ./docs/reference/development.md

## Credits

**Icon:** Designed by [OpenMoji](https://openmoji.org/) – the open-source emoji
and icon project License: [CC BY-SA
4.0](https://creativecommons.org/licenses/by-sa/4.0/#)

**Built with:** [Copier](https://github.com/copier-org/copier) – Template project generator

## License

This project is licensed under the Apache 2.0 License. See the
[LICENSE](https://github.com/navapbc/platform-cli/blob/main/LICENSE) file for
details.

## Community

- [Code of Conduct](https://github.com/navapbc/platform-cli/blob/main/CODE_OF_CONDUCT.md)
- [Contributing Guidelines](https://github.com/navapbc/platform-cli/blob/main/CONTRIBUTING.md)
- [Security Policy](https://github.com/navapbc/platform-cli/blob/main/SECURITY.md)
