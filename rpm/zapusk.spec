Name:           zapusk
Version:        2.9.3
Release:        1%{?dist}
Summary:        Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)
License:        GPLv3+
BuildArch:      noarch
Requires:       python3, python3-pyside6, wine, winetricks, curl, jq,
                p7zip, cabextract, unzip, vulkan-tools
Recommends:     gamemode, mangohud

%description
Zapusk sets up wine prefixes, installs DXVK/VKD3D and Windows dependencies
automatically so any Windows game runs with one click. 10 languages,
any-distro support, FreeBSD Gaming Mode (bhyve passthrough).

%install
mkdir -p %{buildroot}/opt/zapusk %{buildroot}/usr/bin %{buildroot}/usr/share/applications %{buildroot}/usr/share/icons/hicolor/scalable/apps %{buildroot}/usr/share/licenses/%{name}
cp -r zapusk %{buildroot}/opt/zapusk/
cp install.sh requirements.txt %{buildroot}/opt/zapusk/
cat > %{buildroot}/usr/bin/zapusk <<'EOF'
#!/bin/sh
cd /opt/zapusk && exec python3 -m zapusk gui "$@"
EOF
chmod 755 %{buildroot}/usr/bin/zapusk
install -Dm644 zapusk.desktop %{buildroot}/usr/share/applications/zapusk.desktop
install -Dm644 assets/zapusk.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/zapusk.svg
install -Dm644 LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE

%files
/opt/zapusk
%{_bindir}/zapusk
%{_datadir}/applications/zapusk.desktop
%{_datadir}/icons/hicolor/scalable/apps/zapusk.svg
%license /usr/share/licenses/%{name}/LICENSE
