# SPDX-License-Identifier: GPL-3.0-or-later
PORTNAME=	zapusk
DISTVERSION=	3.2.0
DISTVERSIONPREFIX=	v
CATEGORIES=	games

MAINTAINER=	romanepev2014@gmail.com
COMMENT=	Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)
WWW=		https://github.com/romanepev2014-stack/zapusk

LICENSE=	GPLv3+
LICENSE_FILE=	${WRKSRC}/LICENSE

RUN_DEPENDS=	wine-devel>0:emulators/wine-devel \
		winetricks>0:emulators/winetricks \
		${PYTHON_PKGNAMEPREFIX}pyside6>0:devel/pyside6@${PY_FLAVOR}

USES=		python
USE_PYTHON=	autoplist
USE_GITHUB=	yes
GH_ACCOUNT=	romanepev2014-stack
NO_ARCH=	yes
NO_BUILD=	yes

do-install:
	${MKDIR} ${STAGEDIR}${PYTHON_SITELIBDIR}
	cd ${WRKSRC}/src && ${COPYTREE_SHARE} zapusk ${STAGEDIR}${PYTHON_SITELIBDIR}
	${MKDIR} ${STAGEDIR}${PREFIX}/bin
	${PRINTF} '#!/bin/sh\nexec ${PYTHON_CMD} -m zapusk "$$@"\n' > ${STAGEDIR}${PREFIX}/bin/zapusk
	${CHMOD} 755 ${STAGEDIR}${PREFIX}/bin/zapusk
	${MKDIR} ${STAGEDIR}${PREFIX}/share/applications
	${INSTALL_DATA} ${WRKSRC}/assets/zapusk.desktop ${STAGEDIR}${PREFIX}/share/applications/zapusk.desktop
	${MKDIR} ${STAGEDIR}${PREFIX}/share/icons/hicolor/scalable/apps
	${INSTALL_DATA} ${WRKSRC}/assets/zapusk.svg ${STAGEDIR}${PREFIX}/share/icons/hicolor/scalable/apps/zapusk.svg

.include <bsd.port.mk>
