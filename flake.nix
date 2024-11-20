{
  description = "Nava PBC Platform CLI";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      poetry2nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            poetry2nix.overlays.default
            (final: _: {
              inherit nava-platform-cli nava-platform-cli-devEnv;
            })
          ];
        };

        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication
          mkPoetryEnv
          defaultPoetryOverrides
          ;

        # Non-Python runtime dependencies go here
        runtimePackages = with pkgs; [
          gitMinimal
        ];

        # Python packages don't always completely capture their build
        # requirements, this is some convenience functionality to make it easier
        # to fix that on a case-by-case basis to get unblocked (push fixes
        # upstream when you can)
        customPoetryOverrides =
          final: super:
          builtins.mapAttrs
            (
              attr: systems:
              super.${attr}.overridePythonAttrs (old: {
                nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ map (a: final.${a}) systems;
              })
            )
            {
              # https://github.com/nix-community/poetry2nix/blob/master/docs/edgecases.md#modulenotfounderror-no-module-named-packagename
              # package = [ "setuptools" ];
            };

        poetryOverrides = [
          defaultPoetryOverrides
          customPoetryOverrides
        ];

        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        nava-platform-cli = mkPoetryApplication {
          projectDir = self;
          propogatedBuildInputs = runtimePackages;
          overrides = poetryOverrides;
        };

        nava-platform-cli-devEnv = mkPoetryEnv {
          projectDir = self;
          editablePackageSources = {
            "nava-platform-cli" = ./.;
          };
          overrides = poetryOverrides;
          extraPackages =
            ps: with ps; [
              jedi-language-server
              python-lsp-server
              pyflakes
            ];
        };

        # TODO: could add docker-client here?
        generalDevPackages = with pkgs; [
          # dev tooling
          gnumake

          # linting
          shellcheck
          nixfmt-rfc-style

          # python
          # pipx # if wanting to test pipx stuff
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
            pkgs.nava-platform-cli
          ] ++ runtimePackages;
          config = {
            Entrypoint = "docker-entry";
            WorkingDir = "/project-dir";
          };
        };
      in
      {
        packages = {
          default = pkgs.nava-platform-cli;

          docker = pkgs.dockerTools.buildLayeredImage dockerBuildArgs;
          dockerStream = pkgs.dockerTools.streamLayeredImage dockerBuildArgs;
        };

        # nix run .
        apps.default = {
          type = "app";
          program = "${pkgs.nava-platform-cli}/bin/nava-platform";
        };

        devShells = {
          # Shell for general app development.
          #
          #     nix develop
          #
          # Use unless you are hitting issues, in which case see `devTools` below.
          default = pkgs.nava-platform-cli-devEnv.env.overrideAttrs (oldAttrs: {
            buildInputs = generalDevPackages ++ runtimePackages ++ [ pkgs.poetry ];
          });

          # Shell for just dev tools, skipping Python dependencies (which may
          # have issues building, etc.).
          #
          #     nix develop .#devTools
          #
          # Can use this shell for changes to pyproject.toml/poetry.lock or
          # running misc make targets/dev scripts unrelated to Python.
          devTools = pkgs.mkShell { packages = generalDevPackages ++ runtimePackages ++ [ pkgs.poetry ]; };
        };

        legacyPackages = pkgs;
      }
    );
}
