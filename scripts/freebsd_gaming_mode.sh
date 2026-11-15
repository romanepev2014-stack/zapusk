#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# ============================================================================
# ZAPUSK — FreeBSD Gaming Mode (bhyve + GPU passthrough + Looking Glass)
# ---------------------------------------------------------------------------
# EN: prepares a FreeBSD host to run heavy/online games in a Linux (Zen)
#     virtual machine with full GPU speed:
#       1. checks CPU virtualization (VT-d / AMD-Vi)
#       2. finds your GPUs (pciconf)
#       3. writes passthrough (ppt) config into /boot/loader.conf
#       4. generates a ready bhyve start script (IVSHMEM for Looking Glass)
#     Tested-by: nobody yet — YOU are the tester. Logs -> GitHub Issues.
# RU: готовит FreeBSD-хост для запуска тяжёлых/онлайн-игр в Linux-VM (Zen)
#     с полной скоростью видеокарты. Скрипт НЕ тестировался на железе —
#     первый тестер — ты. Логи и ошибки — в Issues на GitHub.
# ============================================================================
set -u
info()  { echo -e "\033[1;36m[GAMING-MODE]\033[0m $*"; }
warn()  { echo -e "\033[1;33m[GAMING-MODE]\033[0m $*"; }
fail()  { echo -e "\033[1;31m[GAMING-MODE]\033[0m $*"; exit 1; }

# --- 0. только FreeBSD и root ---
[ "$(uname -s)" = "FreeBSD" ] || fail "This script is FreeBSD-only / Скрипт только для FreeBSD"
[ "$(id -u)" = "0" ] || fail "Run as root: sudo sh $0"

info "=== Zapusk FreeBSD Gaming Mode ==="
info "FreeBSD $(freebsd-version)"

# --- 1. IOMMU / VT-d ---
info "Checking IOMMU (VT-d / AMD-Vi)…"
if dmesg | grep -qiE "VTD|AMD-Vi|IOMMU"; then
    dmesg | grep -iE "VTD|AMD-Vi|IOMMU" | head -3
    info "✅ IOMMU detected"
else
    warn "⚠ IOMMU NOT detected. Enable VT-d/AMD-Vi in BIOS/UEFI, add to /boot/loader.conf:"
    warn "    vmm_load=\"YES\""
fi

# --- 2. видеокарты ---
info "GPU devices found:"
pciconf -lv | grep -B4 "class=0x03" | grep -E "^\S+@|device|vendor" || warn "no VGA devices?"

cat <<'EOF'

Next / Дальше:
1) Pick the GPU to passthrough (e.g. 0/2/0) from the list above.
   Запиши PCI-адрес карты, которую отдаём VM (например 0/2/0).
   ВАЖНО: у карты обычно 2 функции — VGA (0/2/0) и AUDIO (0/2/1).
   ОТДАВАТЬ НУЖНО ОБЕ.
EOF

read -rp "GPU PCI address (e.g. 0/2/0): " GPU
GPU_AUDIO="${GPU%/*}/$(( ${GPU##*/} + 1 ))"

# --- 3. loader.conf: passthrough устройства ---
LOADER=/boot/loader.conf
info "Writing passthrough devices to $LOADER"
grep -q "pptdevs" "$LOADER" 2>/dev/null && warn "pptdevs already set — merge manually!"
cat >> "$LOADER" <<EOF
vmm_load="YES"
pptdevs="$GPU $GPU_AUDIO"
EOF
info "✅ loader.conf updated (reboot required / нужен reboot)"

# --- 4. сеть для VM (tap) ---
if ! grep -q "net.link.tap.up_on_open" "$LOADER"; then
    echo 'net.link.tap.up_on_open=1' >> "$LOADER"
fi
info "Network: VM will use tap0 + NAT via pf (see guide in README)"

# --- 5. диск VM ---
read -rp "Disk size for the Linux VM (default 120G): " SIZE
SIZE="${SIZE:-120G}"
VMNAME="zapusk-gaming"
ZVOL="zroot/$VMNAME"
if zfs list "$ZVOL" >/dev/null 2>&1; then
    warn "zvol $ZVOL already exists, keeping it"
else
    info "Creating zvol $ZVOL ($SIZE)"
    zfs create -V "$SIZE" "$ZVOL" || fail "zvol creation failed"
fi
DISK="/dev/zvol/$ZVOL"

# --- 6. скрипт запуска VM ---
cat > "/usr/local/bin/${VMNAME}-start.sh" <<EOF
#!/bin/sh
# EN: start the gaming VM / RU: запуск игровой VM
# Download a Linux ISO (e.g. CachyOS/Arch with Zen kernel), install to disk once,
# then boot from disk. IVSHMEM region is shared memory for Looking Glass.
ZVOL="$DISK"
ISO="\$1"   # pass ISO path for first install, omit later

# EN: hugepages for IVSHMEM / RU: огромные страницы для Looking Glass
kldstat -q -m vmware_guest_vmmemctl >/dev/null 2>&1
sysctl -q kern.ipc.shm_allow_removed=1

DEVS="-s 3:0,passthru,$GPU -s 3:1,passthru,$GPU_AUDIO"
MEM="-s 4:0,ivshmem,shm=looking-glass,size=128M"
CD=""
[ -n "\$ISO" ] && CD="-s 5:0,ahci-cd,\$ISO"

bhyve -c 8 -m 16G -H -A -P \\
    -s 0:0,hostbridge \\
    -s 1:0,lpc \\
    -s 2:0,ahci-hd,\$ZVOL \\
    \$DEVS \\
    \$MEM \\
    -s 6:0,virtio-net,tap0 \\
    \$CD \\
    -l com1,stdio \\
    $VMNAME
rc=\$?
bhyvectl --destroy --vm=$VMNAME 2>/dev/null
exit \$rc
EOF
chmod +x "/usr/local/bin/${VMNAME}-start.sh"

# --- 7. авто-запуск VM через rc.d ---
cat > /usr/local/etc/rc.d/zapusk-gaming <<'EOF'
#!/bin/sh
# PROVIDE: zapusk-gaming
# REQUIRE: NETWORKING
# KEYWORD: nojail
. /etc/rc.subr
name="zapusk_gaming"
desc="Zapusk Gaming VM (bhyve)"
command="/usr/local/bin/zapusk-gaming-start.sh"
command_background="YES"
pidfile="/var/run/zapusk-gaming.pid"
load_rc_config $name
run_rc_command "$1"
EOF
chmod +x /usr/local/etc/rc.d/zapusk-gaming

info ""
info "=== DONE / ГОТОВО ==="
cat <<EOF
Next steps / Следующие шаги:
  1. reboot                        # подхватить pptdevs
  2. Скачай ISO с Linux (Zen kernel: CachyOS, Garuda, Arch)
  3. Установи Linux в VM:  ${VMNAME}-start.sh /path/to/linux.iso
     (поставь драйверы GPU, Steam, Proton; поставь Looking Glass host)
  4. Дальше грузись с диска:  ${VMNAME}-start.sh
  5. На хосте собери Looking Glass-клиент (порт emulators/looking-glass
     или исходники с looking-glass.io — cmake, зависимости в README)
  6. Запускай клиент — картинка игры в окне на FreeBSD.
Честно / Honest: VT-d нужен в BIOS, хосту нужен свой вывод (iGPU/слабая карта).
Античиты: почти все работают, Vanguard — нет.
EOF
