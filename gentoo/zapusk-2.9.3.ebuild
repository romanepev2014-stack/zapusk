# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 roma_ogon

EAPI=8

PYTHON_COMPAT=( python3_{11..13} )
DISTUTILS_SINGLE_IMPL=1
inherit python-single-r1

DESCRIPTION="Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)"
HOMEPAGE="https://github.com/romanepev2014-stack/zapusk"
SRC_URI="https://github.com/romanepev2014-stack/zapusk/archive/v${PV}.tar.gz -> ${P}.tar.gz"
LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"
RDEPEND="
    $(python_gen_cond_dep 'dev-python/pyside6[${PYTHON_USEDEP}]')
    app-emulation/wine-staging
    app-emulation/winetricks
    sys-devel/gettext
"
src_install() {
    python_domodule zapusk
    python_newscript - zapusk <<'EOF'
#!/usr/bin/env python3
import sys
from zapusk.cli import main
sys.exit(main())
EOF
    domenu zapusk.desktop
    doicon assets/zapusk.svg
}
