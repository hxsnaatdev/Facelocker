{ config, lib, pkgs, ... }:
let
  cfg = config.programs.facerecGuard;
in {
  options.programs.facerecGuard = {
    enable = lib.mkEnableOption "FaceRec Guard Home Manager configuration";

    projectDir = lib.mkOption {
      type = lib.types.str;
      default = "${config.home.homeDirectory}/projects/facerec";
      description = "Path to the FaceRec Guard project.";
    };
  };

  config = lib.mkIf cfg.enable {
    home.packages = with pkgs; [
      python311
      git
      cmake
      ffmpeg
      pkg-config
    ];

    home.sessionVariables = {
      FACEREC_PROJECT_DIR = cfg.projectDir;
      FACEREC_EMBEDDINGS = "${cfg.projectDir}/data/authorized_faces.json";
    };

    programs.zsh = {
      enable = true;
      shellAliases = {
        facerec-dev = "cd ${cfg.projectDir} && nix develop";
        facerec-test = "cd ${cfg.projectDir} && nix develop -c python -m unittest discover -s tests -p 'test_*.py'";
        facerec-enroll = "cd ${cfg.projectDir} && nix develop -c python -m app.enroll --samples 12 --output data/authorized_faces.json";
        facerec-run = "cd ${cfg.projectDir} && nix develop -c python -m app.main --timeout 10 --fps 5 --embeddings data/authorized_faces.json --show-preview";
      };
    };

    home.file.".config/facerec/config-note.txt".text = ''
      FaceRec Guard Home Manager profile is active.
      Project directory: ${cfg.projectDir}
      Embeddings path: ${cfg.projectDir}/data/authorized_faces.json
    '';
  };
}
