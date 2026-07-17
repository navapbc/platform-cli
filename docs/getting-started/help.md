# Help

## Help pages

For general usage and context, the CLI itself has a variety of helpful content
available. At the top-level:

```sh
nava-platform --help
```

And on every command/sub-command:

```sh
nava-platform infra --help

nava-platform infra install --help
```

## Verbose output

The CLI has multiple levels of information it can provide in its output. The
verbosity of this output can be increased with the `--verbose` or `-v` flag:

```
nava-platform infra install -v ...
```

If a command has more information that could be shared in-line, it will (not all
do), but this will also generally increase the amount of information
[logged](#logs).

The `-v` flag can be repeated for increasing verbosity, for example:

```
nava-platform infra install -vv ...
```

Will starting print some more generic operational info. At `-vvv` the debug
level logs will be printed.

## Logs

As mentioned above, with enough `-v` flags the logs will be printed to the
screen, but the logs ultimately live on your system and you can inspect them at
any time. The exact path with vary [depending on your system][log-path] and/or
possible configuration, but by default should be at:

=== "Linux"

    ```sh
    ~/.local/share/state/nava-platform-cli/log/log.json
    ```

=== "macOS"

    ```sh
    ~/Library/Logs/nava-platform-cli/log.json
    ```

[log-path]: https://platformdirs.readthedocs.io/en/latest/platforms.html#user-log-dir

## Open an issue

If you encounter an error using the tool (or find an error in the
documentation), the [GitHub issues for the project][gh-issues] are a good place
to search if others have encountered the same, or to file a new issue for what
you are seeing if no existing ones match.

[gh-issues]: https://github.com/navapbc/platform-cli/issues
