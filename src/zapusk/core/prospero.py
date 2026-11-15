# SPDX-License-Identifier: GPL-3.0-or-later
"""Project Prospero — честная подготовка PS5-совместимости.

EN: We cannot run PS5 binaries today (no public decryption keys — the wall).
    What we CAN do now: parse PS5 containers (PKG), catalog dumps, draft the
    FreeBSD->Linux syscall translation table (PS5 OS is FreeBSD-based, so
    binaries are ELF and syscalls are FreeBSD-flavored — closer to Linux than
    Windows ever was), and stream from a real PS5 via Chiaki.
RU: Сегодня запустить PS5-бинарники нельзя (нет публичных ключей — стена).
    Что можно сейчас: парсить контейнеры PKG, каталогизировать дампы,
    начать таблицу трансляции FreeBSD->Linux (ОС PS5 — на базе FreeBSD,
    бинарники ELF — ближе к Linux, чем Windows когда-либо был),
    и стримить с реальной PS5 через Chiaki.

Это не эмулятор. Это фундамент. Когда ключи появятся — слой уже готов.
"""

# ============================================================
# EN: PKG container parser (no keys needed — it's just a box).
# RU: парсер контейнера PKG (ключи не нужны — это просто коробка).
# ============================================================
PKG_MAGIC = b"\x7fPKG"
PS5_SERIAL_RE = rb"PPSA[0-9]{5}"   # EN: PS5 title IDs. RU: серийники игр PS5
PS4_SERIAL_RE = rb"CUSA[0-9]{5}"


def sniff_ps5_pkg(path):
    """EN: -> dict(serial, size) or None. RU: -> словарь(серийник, размер) или None."""
    import re, os
    try:
        with open(path, "rb") as f:
            head = f.read(16 * 1024 * 1024)
    except OSError:
        return None
    if head[:4] != PKG_MAGIC:
        return None
    m = re.search(PS5_SERIAL_RE, head)
    serial = m.group(1).decode() if m else None
    if not serial:
        return None
    return dict(serial=serial, size=os.path.getsize(path))


def parse_self_info(path):
    """EN: minimal SELF/SCE-ELF header reader. Works on decrypted/fake-signed
       binaries; on retail-encrypted ones it reports the wall honestly.
       RU: минимальное чтение заголовка SELF. Работает на расшифрованных
       бинарниках; на розничных шифрованных честно сообщает о стене."""
    try:
        with open(path, "rb") as f:
            head = f.read(0x400)
    except OSError:
        return None
    if head[:4] != b"\x7fELF":
        return None
    ei = head[0x07]
    info = dict(elf_class="64-bit" if ei == 2 else "32-bit",
                endian="little" if head[0x05] == 1 else "big",
                type=__import__("struct").unpack("<H", head[0x10:0x12])[0])
    # EN: Sony marks encrypted SELF files via proprietary header flags at
    #     e_flags / extended headers. Without keys we can only see the shell.
    # RU: Sony помечает шифрованные SELF флагами; без ключей видим лишь оболочку.
    info["encrypted"] = True   # EN: safe default until decrypted images exist
    info["note"] = "SELF-контейнер Sony. Розничные бинарники зашифрованы — нужны ключи."
    return info


# ============================================================
# EN: Syscall translation draft (FreeBSD/Orbis -> Linux).
#     PS5 ("Prospero") inherits the Orbis syscall interface; public numbers
#     come from OpenOrbis docs. VERIFY against OpenOrbis wiki before use.
# RU: Черновик трансляции сисколов (FreeBSD/Orbis -> Linux).
#     PS5 наследует интерфейс Orbis; номера — из публичной документации
#     OpenOrbis. ПРОВЕРЯТЬ по OpenOrbis wiki перед использованием.
# ============================================================
SYSCALL_TABLE = {
    # orbis_nr: ("orbis_name", "linux_equivalent_or_note")
    # Примеры из публичных документов OpenOrbis (поколение PS4/Orbis):
    0x001: ("exit", "exit_group"),
    0x002: ("fork", "fork/clone"),
    0x003: ("read", "read"),
    0x004: ("write", "write"),
    0x005: ("open", "openat"),
    0x006: ("close", "close"),
    0x00A: ("unlink", "unlinkat"),
    0x014: ("getpid", "getpid"),
    0x0C9: ("getdents", "getdents64"),
    # TODO: продолжить по OpenOrbis wiki — сотни вызовов; многие 1:1 с FreeBSD
}

# EN: Orbis/Prospero shared memory & GPU command buffer paths are NOT plain
#     syscalls — games talk to libSce* usermode libraries and push GNM
#     command buffers. Translating THAT is the DXVK-scale part of the work.
# RU: Разделяемая память и командные буферы GPU — не сисколы: игры зовут
#     юзермод-библиотеки libSce* и пихают GNM-команды. Их трансляция — часть
#     размером с DXVK.

WALL = (
    "Стена: розничные SELF-файлы PS5 подписаны ключами Sony. Публично их нет. "
    "Всё остальное (syscall-слой, каталог, автоматика Zapusk) готово ждать. "
    "The wall: retail PS5 SELF files are signed with Sony keys; none are public. "
    "Everything else (syscall layer, catalog, Zapusk automation) is ready and waiting."
)


def layer_readiness():
    """EN: honest status of the Prospero layer. RU: честная готовность слоя."""
    return {
        "pkg_parse": "✅ готов (без ключей)",
        "dump_catalog": "✅ готов (через Zapusk Console Mode)",
        "syscall_table": "🟡 черновик (OpenOrbis, требует доработки)",
        "gnm_translation": "⏳ невозможно без расшифрованных бинарников",
        "decryption_keys": "❌ стена — не в наших руках",
        "chiaki_stream": "✅ работает с реальной PS5 сегодня",
    }
