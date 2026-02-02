{
    description = "FastAPI dev environment (Nixpkgs only)";

    inputs = {
        nixpkgs.url = "github:nixOS/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs =
        {
            self,
            nixpkgs,
            flake-utils,
        }:
        flake-utils.lib.eachDefaultSystem (
            system:
            let
                pkgs = import nixpkgs { inherit system; };

                pythonEnv = pkgs.python3.withPackages (
                    ps: with ps; [
                        fastapi
                        asyncpg
                        uvicorn
                        pydantic
                        requests
                        sqlmodel
                    ]
                );
            in
            {
                devShells.default = pkgs.mkShell {
                    packages = [ pythonEnv ];
                    shellHook = "export NIX_SHELL_NAME='webbfarstun'";
                };
            }
        );
}
