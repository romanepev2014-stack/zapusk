{
  description = "Zapusk — cyberpunk launcher for Windows games (Wine + DXVK auto-setup)";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f (import nixpkgs { inherit system; }));
    in
    {
      packages = forAllSystems (pkgs: {
        default = pkgs.python3Packages.buildPythonApplication {
          pname = "zapusk";
          version = "2.9.2";
          src = ./.;
          propagatedBuildInputs = [ pkgs.python3Packages.pyside6 ];
          makeWrapperArgs = [ "--set" "ZAPUSK_NO_INSTALL_HINT" "1" ];
          postInstall = ''
            mkdir -p $out/share/applications $out/share/icons/hicolor/scalable/apps
            cp zapusk.desktop $out/share/applications/
            cp assets/zapusk.svg $out/share/icons/hicolor/scalable/apps/zapusk.svg
          '';
          meta = with pkgs.lib; {
            description = "Windows games launcher for Linux/FreeBSD";
            license = licenses.gpl3Plus;
            platforms = platforms.linux;
          };
        };
      });
    };
}
