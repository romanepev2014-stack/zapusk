# Maintainer: roma_ogon
pkgname=zapusk
pkgver=2.9.1
pkgrel=1
pkgdesc="Cyberpunk launcher for Windows games on Arch Linux (Wine + DXVK + VKD3D)"
arch=('any')
url="https://github.com/roma_ogon/zapusk"
license=('GPL-3.0-or-later')
depends=('python' 'pyside6' 'wine-staging' 'winetricks' 'dxvk'
         'vulkan-icd-loader' 'lib32-vulkan-icd-loader' 'curl' 'jq'
         'cabextract' 'unzip' 'p7zip')
optdepends=('nvidia-utils: NVIDIA Vulkan (root)'
            'lib32-nvidia-utils: NVIDIA Vulkan (32-bit)'
            'vulkan-radeon: AMD Vulkan'
            'lib32-vulkan-radeon: AMD Vulkan (32-bit)'
            'vulkan-intel: Intel Vulkan'
            'lib32-vulkan-intel: Intel Vulkan (32-bit)'
            'gamemode: performance daemon'
            'lib32-gamemode: performance daemon (32-bit)'
            'mangohud: FPS overlay'
            'lib32-mangohud: FPS overlay (32-bit)'
            'vkd3d-proton: DirectX 12 support')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
  install -dm755 "$pkgdir/opt/zapusk"
  cp -r "$srcdir/$pkgname-$pkgver/zapusk" "$pkgdir/opt/zapusk/"
  cp "$srcdir/$pkgname-$pkgver/install_arch.sh" \
     "$srcdir/$pkgname-$pkgver/requirements.txt" "$pkgdir/opt/zapusk/"
  install -Dm755 "$srcdir/$pkgname-$pkgver/run.sh" "$pkgdir/opt/zapusk/run.sh"

  install -dm755 "$pkgdir/usr/bin"
  printf '#!/bin/sh\ncd /opt/zapusk && exec python -m zapusk gui "$@"\n' > "$pkgdir/usr/bin/zapusk"
  chmod 755 "$pkgdir/usr/bin/zapusk"

  install -Dm644 "$srcdir/$pkgname-$pkgver/zapusk.desktop" "$pkgdir/usr/share/applications/zapusk.desktop"
  install -Dm644 "$srcdir/$pkgname-$pkgver/assets/zapusk.svg" "$pkgdir/usr/share/icons/hicolor/scalable/apps/zapusk.svg"
  install -Dm644 "$srcdir/$pkgname-$pkgver/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
