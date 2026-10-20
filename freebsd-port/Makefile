# SPDX-License-Identifier: GPL-3.0-or-later
PORTNAME=	zapusk
DISTVERSION=	2.9.2
CATEGORIES=	games
MASTER_SITES=	https://github.com/romanepev2014-stack/${PORTNAME}/archive/refs/tags/
DISTNAME=	v${DISTVERSION}

MAINTAINER=	romanepev2014@gmail.com
COMMENT=	Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)
WWW=		https://github.com/romanepev2014-stack/zapusk

LICENSE=	GPLv3+
LICENSE_FILE=	${WRKSRC}/LICENSE

RUN_DEPENDS=	wine-devel>0:emulators/wine-devel \
		winetricks>0:emulators/winetricks \
		${PYTHON_PKGNAMEPREFIX}pyside6>0:devel/pyside6@${PY_FLAVOR}

USES=		python
USE_PYTHON=	autoplist distutils noflavor
NO_ARCH=	yes

post-install:
	${MKDIR} ${STAGEDIR}${PREFIX}/share/applications
	${INSTALL_DATA} ${WRKSRC}/zapusk.desktop ${STAGEDIR}${PREFIX}/share/applications/
	${MKDIR} ${STAGEDIR}${PREFIX}/share/icons/hicolor/scalable/apps
	${INSTALL_DATA} ${WRKSRC}/assets/zapusk.svg ${STAGEDIR}${PREFIX}/share/icons/hicolor/scalable/apps/zapusk.svg

.include <bsd.port.mk>
