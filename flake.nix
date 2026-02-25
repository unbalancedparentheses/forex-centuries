{
  description = "forex-centuries — Historical FX data spanning nine centuries";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3.withPackages (ps: [
          ps.pandas
          ps.openpyxl
          ps.matplotlib
          ps.scipy
          ps.pytest
          ps.jupyterlab
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [ python ];
        };
      }
    );
}
