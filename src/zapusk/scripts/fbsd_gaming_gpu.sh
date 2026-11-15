#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# ============================================================================
# ZAPUSK — FreeBSD Gaming GPU Layer
# EN: the "individual FreeBSD for gaming" idea:
#     - detect your actual GPU (pciconf), install exactly its driver
#     - REMOVE drivers you don't need (clean stack, like you asked)
#     - remember hardware fingerprint — swap the card, next run auto-fixes
#     - optional: generate a tuned kernel config (Zen-style) and build it
#     Games run on the host GPU through wine-devel + DXVK — no passthrough
#     needed for the light/medium ones.
# RU: идея «индивидуальной FreeBSD для игр»:
#     - определяем реальную видеокарту, ставим ТОЛЬКО её драйвер
#     - УДАЛЯЕМ ненужные (чистый стек)
#     - отпечаток железа: поменял карту -> следующий запуск всё починит
#     - опционально: тюнингованный конфиг ядра и сборка
# ============================================================================
set -u
[ "$(uname -s)" = "FreeBSD" ] || { echo "❌ только FreeBSD / FreeBSD only"; exit 1; }
[ "$(id -u)" = "0" ] || exec sudo sh "$0" "$@"
info(){ echo -e "\033[1;36m[GPU]\033[0m $*"; }
ok()  { echo -e "\033[1;32m[GPU]\033[0m $*"; }
warn(){ echo -e "\033[1;33m[GPU]\033[0m $*"; }

FP=/var/db/zapusk-gpu.fingerprint

# --- 1. детект железа ---
info "Сканирую PCI..."
VGA=$(pciconf -lv | grep -B2 "class=0x03" | grep -E "vendor|device" | tr '\n' ' ')
VENDOR=$(pciconf -lv | awk '/class=0x03/{f=1} f&&/vendor/{match($0,/0x[0-9a-f]+/); print substr($0,RSTART,RLENGTH); exit}' | head -1)
DEVICE=$(pciconf -lv | awk '/class=0x03/{f=1} f&&/device/{match($0,/0x[0-9a-f]+/); print substr($0,RSTART,RLENGTH); exit}' | head -1)
info "GPU: ${VENDOR:-?}:${DEVICE:-?}"

CUR_FP="${VENDOR:-none}:${DEVICE:-none}"
if [ -f "$FP" ] && [ "$(cat "$FP")" != "$CUR_FP" ]; then
    warn "Железо изменилось ($(cat "$FP") -> $CUR_FP)! Перенастраиваю драйверы..."
    CHANGED=1
else
    CHANGED=0
fi
echo "$CUR_FP" > "$FP"

# --- 2. выбор стека под вендора ---
case "$VENDOR" in
  0x10de) WANT="nvidia-driver nvidia-settings nvidia-xconfig"; WANT_KLD="nvidia-modeset"; CLEAN="drm-kmod xf86-video-amdgpu xf86-video-intel" ;;
  0x1002|0x1022) WANT="drm-kmod mesa-dri mesa-libs libva-intel-driver"; WANT_KLD="amdgpu"; CLEAN="nvidia-driver nvidia-settings nvidia-xconfig" ;;
  0x8086) WANT="drm-kmod mesa-dri mesa-libs libva-intel-driver"; WANT_KLD="i915kms"; CLEAN="nvidia-driver nvidia-settings nvidia-xconfig" ;;
  *) warn "Вендор $VENDOR не опознан — ставлю универсальный стек (drm-kmod)"; WANT="drm-kmod mesa-dri mesa-libs"; WANT_KLD="amdgpu"; CLEAN="nvidia-driver" ;;
esac

# --- 3. ставим нужное ---
info "Ставлю нужное: $WANT"
pkg install -y $WANT || warn "часть пакетов не встала"

# --- 4. удаляем ненужное (как ты просил) ---
for p in $CLEAN; do
    if pkg info "$p" >/dev/null 2>&1; then
        info "Удаляю ненужный драйвер: $p"
        pkg delete -y "$p" || true
    fi
done

# --- 5. грузим модуль и вешаем на автозагрузку ---
for m in $WANT_KLD; do
    sysrc -q kld_list+=" $m" 2>/dev/null || echo "kld_list+=\" $m\"" >> /etc/rc.conf
    kldload "$m" 2>/dev/null || true
done

# --- 6. vulkan + игровой стек ---
info "Vulkan и игровой стек..."
pkg install -y vulkan-tools mesa-vulkan-drivers wine-devel winetricks gamemode || warn "часть не встала"

# --- 7. опционально: тюнинг ядра (Zen-стиль) ---
if [ "${1:-}" = "--kernel" ]; then
    if [ -d /usr/src/sys ]; then
        info "Генерирую конфиг ядра ZAPUSK (include GENERIC + тюнинг)..."
        cat > /usr/src/sys/amd64/conf/ZAPUSK <<'EOF'
# Zapusk gaming kernel — включает GENERIC и добавляет тюнинг.
# Собрать: cd /usr/src && make -j$(sysctl -n hw.ncpu) buildkernel KERNCONF=ZAPUSK
#          make installkernel KERNCONF=ZAPUSK   (потом reboot)
include GENERIC
ident   ZAPUSK

# EN: game-friendly scheduling & timing. RU: игровой тюнинг.
options SCHED_ULE
options KBD_INSTALL_CDEV
options PREEMPTION            # EN: full kernel preemption if supported (14+/15). RU: вытеснение ядра
options NULLFS
options TMPFS

# EN: crash dumps off — no waiting after a game crash. RU: без дампов — быстрее.
nooptions KDB
nooptions DDB
nooptions GDB
EOF
        ok "Конфиг готов: /usr/src/sys/amd64/conf/ZAPUSK"
        info "Собираю ядро (это 30-60 минут)..."
        (cd /usr/src && make -j"$(sysctl -n hw.ncpu)" buildkernel KERNCONF=ZAPUSK && make installkernel KERNCONF=ZAPUSK) \
            && ok "Ядро установлено — перезагрузись" || warn "сборка не удалась — конфиг остался, попробуй вручную"
    else
        warn "нет /usr/src — поставь исходники: pkg install -y src"
    fi
fi

# --- 8. проверка ---
info "Проверяю Vulkan..."
vulkaninfo --summary 2>/dev/null | grep -m1 deviceName && ok "Vulkan работает ✅" || warn "Vulkan молчит — перезагрузись и проверь: vulkaninfo"

[ "$CHANGED" = "1" ] && warn "Железо менялось — рекомендую reboot"
ok "Готово. Запуск игр — через обычную видяху: zapusk / wine + DXVK (проброс нужен только для тяжёлых)."
