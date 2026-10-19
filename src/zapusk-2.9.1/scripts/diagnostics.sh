#!/usr/bin/env bash
# Быстрая диагностика без Python
echo "=== Vulkan ==="; vulkaninfo --summary 2>/dev/null | grep -E "GPU|apiVersion|deviceName" || echo "❌ vulkaninfo не работает"
echo "=== 32-bit Vulkan ==="; ls /usr/lib32/libvulkan.so* 2>/dev/null || echo "❌ lib32-vulkan нет"
echo "=== Wine ==="; wine --version 2>/dev/null || echo "❌ wine нет"
echo "=== DXVK ==="; ls /usr/share/dxvk 2>/dev/null || echo "❌ dxvk нет"
echo "=== VKD3D ==="; ls /usr/share/vkd3d-proton 2>/dev/null || echo "❌ vkd3d-proton нет"
echo "=== Пакеты ==="; pacman -Q wine-staging winetricks dxvk vkd3d-proton gamemode mangohud 2>/dev/null
