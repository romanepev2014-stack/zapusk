#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: build .rpm (Fedora/RHEL/openSUSE). RU: сборка .rpm.
set -e
cd "$(dirname "$0")"
command -v rpmbuild >/dev/null || { sudo dnf install -y rpm-build || sudo zypper install -y rpm-build || sudo apt install -y rpm; }
rm -rf rpm-build
mkdir -p rpm-build/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
VER=$(grep -m1 Version: rpm/zapusk.spec | awk '{print $2}')
tar czf "rpm-build/SOURCES/zapusk-$VER.tar.gz" --transform "s,^,zapusk-$VER/," \
    zapusk install.sh requirements.txt zapusk.desktop assets LICENSE
cp rpm/zapusk.spec rpm-build/SPECS/
rpmbuild --define "_topdir $(pwd)/rpm-build" -bb rpm-build/SPECS/zapusk.spec
echo "✅ RPM готов: $(find rpm-build/RPMS -name '*.rpm')"
