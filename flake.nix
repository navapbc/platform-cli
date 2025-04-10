{
  description = "Nava PBC Platform CLI";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix_hammer_overrides = {
      url = "github:TyberiusPrime/uv2nix_hammer_overrides";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      uv2nix_hammer_overrides,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        # Non-Python runtime dependencies go here
        runtimePackages = with pkgs; [
          gitMinimal
        ];

        # uv2nix stuff --------------------------------------------------------

        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        # Create package overlay from workspace.
        overlay = workspace.mkPyprojectOverlay {
          # Prefer prebuilt binary wheels as a package source.
          # Sdists are less likely to "just work" because of the metadata missing from uv.lock.
          # Binary wheels are more likely to, but may still require overrides for library dependencies.
          sourcePreference = "wheel"; # or sourcePreference = "sdist";
          # Optionally customise PEP 508 environment
          # environ = {
          #   platform_release = "5.10.65";
          # };
        };

        # Extend generated overlay with build fixups
        #
        # Uv2nix can only work with what it has, and uv.lock is missing essential metadata to perform some builds.
        # This is an additional overlay implementing build fixups.
        # See:
        # - https://adisbladis.github.io/uv2nix/FAQ.html
        pyprojectOverrides = final: prev: {
          # Implement build fixups here.
          # Note that uv2nix is _not_ using Nixpkgs buildPythonPackage.
          # It's using https://pyproject-nix.github.io/pyproject.nix/build.html
        };

        python = pkgs.python312;

        # Construct package set
        pythonSet =
          # Use base package set from pyproject.nix builders
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              pkgs.lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
                (uv2nix_hammer_overrides.overrides pkgs)
                pyprojectOverrides
              ]
            );

        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        nava-platform-cli-env = pythonSet.mkVirtualEnv "nava-platform-cli-env" workspace.deps.default;

        # TODO: inject runtimePackages here?
        nava-platform-cli = (pkgs.callPackages pyproject-nix.build.util { }).mkApplication {
          venv = nava-platform-cli-env;
          package = pythonSet.nava-platform-cli;
        };

        # TODO: could add docker-client here?
        generalDevPackages = with pkgs; [
          # dev tooling
          gnumake

          # linting
          shellcheck
          nixfmt-rfc-style
          actionlint

          # container things
          skopeo
        ];

        dockerEntryPkg =
          let
            scriptDeps = [
              pkgs.coreutils # for id, stat
              pkgs.util-linux # for setpriv
            ];
          in
          pkgs.stdenv.mkDerivation {
            name = "docker-entry";
            src = pkgs.lib.fileset.toSource {
              root = ./.;
              fileset = ./bin/docker-entry;
            };
            nativeBuildInputs = [ pkgs.makeWrapper ];
            installPhase = ''
              mkdir -p $out/bin
              install $src/bin/docker-entry $out/bin/docker-entry

              wrapProgram $out/bin/docker-entry --prefix PATH : ${pkgs.lib.makeBinPath scriptDeps}
            '';
          };

        dockerBuildArgs = {
          name = "nava-platform-cli";
          tag = "latest";
          contents = [
            dockerEntryPkg
            nava-platform-cli
          ] ++ runtimePackages;
          config = {
            Entrypoint = "docker-entry";
            WorkingDir = "/project-dir";
          };
        };

        nava-platform-cli-docs-env = pythonSet.mkVirtualEnv "nava-platform-cli-docs-env" workspace.deps.groups;

        cli-docs-site = pkgs.stdenv.mkDerivation {
          name = "nava-platform-cli-docs";
          src = pkgs.lib.fileset.toSource {
            root = ./.;
            fileset = pkgs.lib.fileset.unions ([
              ./docs
              ./nava
              ./Makefile
              ./mkdocs.yml
              ./README.md
            ]);
          };
          buildInputs = [ nava-platform-cli-docs-env ] ++ [ pkgs.gnumake ];

          PY_RUN = "";
          buildPhase = ''
            make docs
          '';

          installPhase = ''
            cp -rf site/ $out
          '';

        };
      in
      rec {
        packages = {
          default = nava-platform-cli;
          nava-platform-cli = nava-platform-cli;
          docs = cli-docs-site;

          docker = pkgs.dockerTools.buildLayeredImage dockerBuildArgs;
          dockerStream = pkgs.dockerTools.streamLayeredImage dockerBuildArgs;
        };

        # nix run .
        apps = {
          default = apps.nava-platform-cli;
          nava-platform-cli = {
            type = "app";
            program = "${nava-platform-cli}/bin/nava-platform";
          };
        };

        devShells = {
          # Shell for general app development.
          #
          #     nix develop
          #
          # Use unless you are hitting issues, in which case see `devTools` below.
          default =
            let
              # Create an overlay enabling editable mode for all local dependencies.
              editableOverlay = workspace.mkEditablePyprojectOverlay {
                # Use environment variable
                root = "$REPO_ROOT";
                # Optional: Only enable editable for these packages
                # members = [ "hello-world" ];
              };

              # Override previous set with our overrideable overlay.
              editablePythonSet = pythonSet.overrideScope (
                pkgs.lib.composeManyExtensions [
                  editableOverlay

                  # Apply fixups for building an editable package of your workspace packages
                  (final: prev: {
                    nava-platform-cli = prev.nava-platform-cli.overrideAttrs (old: {
                      # It's a good idea to filter the sources going into an editable build
                      # so the editable package doesn't have to be rebuilt on every change.
                      src = pkgs.lib.fileset.toSource {
                        root = old.src;
                        fileset = pkgs.lib.fileset.unions [
                          (old.src + "/pyproject.toml")
                          (old.src + "/README.md")
                          (old.src + "/nava/__init__.py")
                        ];
                      };

                      # Hatchling (our build system) has a dependency on the `editables` package when building editables.
                      #
                      # In normal Python flows this dependency is dynamically handled, and doesn't need to be explicitly declared.
                      # This behaviour is documented in PEP-660.
                      #
                      # With Nix the dependency needs to be explicitly declared.
                      nativeBuildInputs =
                        old.nativeBuildInputs
                        ++ final.resolveBuildSystem {
                          editables = [ ];
                        };
                    });

                  })
                ]
              );

              # Build virtual environment, with local packages being editable.
              #
              # Enable all optional dependencies for development.
              virtualenv = editablePythonSet.mkVirtualEnv "nava-platform-cli-dev-env" workspace.deps.all;
            in
            pkgs.mkShell {
              inputsFrom = [ devShells.devTools ];
              packages = [ virtualenv ];

              env = {
                # Don't create venv using uv
                UV_NO_SYNC = "1";

                # Force uv to use Python interpreter from venv
                UV_PYTHON = "${virtualenv}/bin/python";

                # For Make targets, Python things will be available directly, so
                # prefer that over running through uv
                PY_RUN = "";
              };

              shellHook = ''
                # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
                export REPO_ROOT=$(git rev-parse --show-toplevel)
              '';
            };

          # Shell for just dev tools, skipping Python dependencies (which may
          # have issues building, etc.).
          #
          #     nix develop .#devTools
          #
          # Can use this shell for changes to pyproject.toml/poetry.lock or
          # running misc make targets/dev scripts unrelated to Python.
          devTools = pkgs.mkShell {
            packages =
              generalDevPackages
              ++ runtimePackages
              ++ [
                uv2nix.packages."${system}".uv-bin
              ];

            env = {
              # Force uv to use nixpkgs Python interpreter
              UV_PYTHON = python.interpreter;
            } // pkgs.lib.optionalAttrs pkgs.stdenv.isLinux {
                # Python libraries often load native shared objects using dlopen(3).
                # Setting LD_LIBRARY_PATH makes the dynamic library loader aware of libraries without using RPATH for lookup.
                LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
              };

            shellHook = ''
              # Undo dependency propagation by nixpkgs.
              unset PYTHONPATH

              # Disable uv Python interpreter fetching, use nix provided one
              export UV_PYTHON_PREFERENCE=only-system;
              export UV_PYTHON_DOWNLOADS=never;
            '';
          };

          # Shell for pipx interaction. For testing installing the package via
          # pipx or other needs.
          pipx = pkgs.mkShell {
            packages = [
              pkgs.pipx
            ];
          };
        };

        legacyPackages = pkgs;
      }
    );
}
