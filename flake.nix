{
  description = "Delicious Enterprise Resource Planning";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, flake-utils, nixpkgs }:
    {
      overlays.default = final: prev: {
        inherit (self.packages.${prev.system}) derp;
      };
    } // flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        poetryOverrides = with pkgs;
          poetry2nix.overrides.withDefaults (final: prev: {
            django-admin = prev.django-admin.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            django-computedfields = prev.django-computedfields.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            django-excel-response2 = prev.django-excel-response2.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            django-fast-update = prev.django-fast-update.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            django-six = prev.django-six.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            excel-base = prev.excel-base.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            screen = prev.screen.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
            sqlparse = prev.sqlparse.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.flit-core ]; });
            timeconvert = prev.timeconvert.overrideAttrs
              (oldAttrs: { buildInputs = [ prev.setuptools ]; });
          });

      in {
        packages.derp = with pkgs;
          poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            overrides = poetryOverrides;

            doCheck = true;
            checkPhase = ''
              runHook preCheck

              # TODO

              runHook postCheck
            '';

            meta = {
              description = "Delicious Enterprise Resource Planning";
              license = lib.licenses.agpl3Only;
            };
          };

        packages.default = self.packages.${system}.derp;

        devShells.default = with pkgs;
          let
            poetryEnv = poetry2nix.mkPoetryEnv {
              projectDir = ./.;
              overrides = poetryOverrides;
            };
          in mkShell {
            propagatedBuildInputs = [ poetryEnv ];
            buildInputs = [ poetry shellcheck python3Packages.black ];
          };
      });
}
