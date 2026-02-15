{
  description = "FaceRec Guard development and Home Manager setup";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, home-manager }:
    let
      mkPkgs = system: import nixpkgs {
        inherit system;
        config.allowUnfree = false;
      };
    in
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = mkPkgs system;
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          numpy
          opencv4
          face_recognition
        ]);
      in
      {
        formatter = pkgs.alejandra;

        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.cmake
            pkgs.ffmpeg
            pkgs.git
            pkgs.pkg-config
          ];

          shellHook = ''
            export PIP_DISABLE_PIP_VERSION_CHECK=1
            export PYTHONDONTWRITEBYTECODE=1
            echo "FaceRec Guard dev shell ready."
            echo "Run tests: python -m unittest discover -s tests -p 'test_*.py'"
          '';
        };
      }))
    // {
      homeConfigurations."ariz@facerec" = home-manager.lib.homeManagerConfiguration {
        pkgs = mkPkgs "aarch64-darwin";
        modules = [
          ./nix/home-manager/home.nix
          {
            home.username = "ariz";
            home.homeDirectory = "/Users/ariz";
            home.stateVersion = "24.11";

            programs.facerecGuard = {
              enable = true;
              projectDir = "/Users/ariz/projects/facerec";
            };
          }
        ];
      };
    };
}
