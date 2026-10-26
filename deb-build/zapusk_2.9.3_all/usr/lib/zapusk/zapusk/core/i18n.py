# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: i18n — UI translations. RU: i18n — переводы интерфейса."""
import json, pathlib
from zapusk.core.util import DATA_DIR, ensure_dirs

CONFIG = DATA_DIR / "config.json"

# EN: code -> (native name, flag). RU: код -> (название, флаг)
LANGS = {
    "ru": ("Русский", "🇷🇺"), "en": ("English", "🇬🇧"),
    "de": ("Deutsch", "🇩🇪"), "fr": ("Français", "🇫🇷"),
    "es": ("Español", "🇪🇸"), "pt": ("Português", "🇵🇹"),
    "uk": ("Українська", "🇺🇦"), "pl": ("Polski", "🇵🇱"),
    "zh": ("Chinese", "🇨🇳"), "ja": ("Japanese", "🇯🇵"),
}

T = {
"en": {
 "Library":"Library","Updates":"Updates","Optimization":"Optimization","Setup":"Setup","Logs":"Logs",
 "My games":"My games","Add game":"Add game","Refresh":"Refresh","Fix & Launch":"Fix & Launch","Launch":"Launch",
 "Drop hint":"Drag & drop an .exe or a game folder here",
 "Empty":"Empty. Click «+ Add» or drag an .exe in.",
 "New game":"New game","Name":"Name","Path to exe":"Path to .exe","Browse":"Browse…","Scan folder":"Scan folder",
 "Preset":"Preset","Own prefix":"Own prefix (recommended for AAA)","Arguments":"Arguments","Add":"Add",
 "Settings":"Settings","Work dir":"Work dir","Virtual desktop":"Virtual desktop (empty = off)","Save":"Save",
 "Game folder":"Game folder","Prefix":"Prefix","Remove":"Remove",
 "GameMode":"GameMode (CPU/IO priority)","MangoHUD":"MangoHUD (FPS overlay)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"DXVK HUD","Wine debug":"Wine debug log","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (runner for tough games)","Download latest":"Download latest",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Check","Update pm":"Update (package manager)",
 "Governor":"CPU governor (performance = less FPS drops)","Enable Perf":"Enable Performance",
 "Swappiness":"Swappiness (10 = less stutter)","Set 10":"Set 10","GameMode daemon":"GameMode daemon",
 "Enable":"Enable","Shader cache":"Shader cache (clear after changing DXVK)","Clear":"Clear",
 "Optimization title":"System optimization","Install all":"Install everything automatically",
 "Check system":"Check system","Setup desc":"One-time system setup (Wine, DXVK, Vulkan drivers).",
 "Logs title":"Logs — pick a game:","No log":"No log yet — launch the game.",
 "Launched":"Launched","Log":"Log","Not starting":"Not starting? Open 📋 logs.",
 "Language":"Language","Theme":"Theme",
},
"ru": {
 "Library":"Библиотека","Updates":"Обновления","Optimization":"Оптимизация","Setup":"Установка","Logs":"Логи",
 "My games":"Мои игры","Add game":"Добавить игру","Refresh":"Обновить","Fix & Launch":"Починить и запустить","Launch":"Запуск",
 "Drop hint":"Перетащи .exe или папку с игрой сюда",
 "Empty":"Пусто. Нажми «＋ Добавить» или перетащи .exe.",
 "New game":"Новая игра","Name":"Название","Path to exe":"Путь к .exe","Browse":"Обзор…","Scan folder":"Сканировать папку",
 "Preset":"Пресет","Own prefix":"Отдельный префикс (рекомендуется для AAA)","Arguments":"Аргументы","Add":"Добавить",
 "Settings":"Настройки","Work dir":"Рабочая папка","Virtual desktop":"Виртуальный рабочий стол (пусто = выкл)","Save":"Сохранить",
 "Game folder":"Папка игры","Prefix":"Префикс","Remove":"Удалить",
 "GameMode":"GameMode (приоритет CPU/IO)","MangoHUD":"MangoHUD (оверлей FPS)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"DXVK HUD","Wine debug":"Wine debug-лог","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (раннер для сложных игр)","Download latest":"Скачать последний",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Проверить","Update pm":"Обновить (пакетный менеджер)",
 "Governor":"CPU governor (performance — меньше просадок FPS)","Enable Perf":"Включить Performance",
 "Swappiness":"Swappiness (10 — меньше фризов)","Set 10":"Установить 10","GameMode daemon":"GameMode (демон)",
 "Enable":"Включить","Shader cache":"Кэш шейдеров (чистить после смены DXVK)","Clear":"Очистить",
 "Optimization title":"Оптимизация системы","Install all":"Установить всё автоматически",
 "Check system":"Проверить систему","Setup desc":"Один раз: системный стек (Wine, DXVK, Vulkan-драйверы).",
 "Logs title":"Логи — выбери игру:","No log":"Лога нет — запусти игру.",
 "Launched":"Запущено","Log":"Лог","Not starting":"Не стартует? Открой 📋 логи.",
 "Language":"Язык","Theme":"Тема",
},
"de": {
 "Library":"Bibliothek","Updates":"Updates","Optimization":"Optimierung","Setup":"Einrichtung","Logs":"Logs",
 "My games":"Meine Spiele","Add game":"Spiel hinzufügen","Refresh":"Aktualisieren","Fix & Launch":"Reparieren & Starten","Launch":"Start",
 "Drop hint":"Ziehe eine .exe oder einen Spieleordner hierher",
 "Empty":"Leer. Klicke auf «+ Hinzufügen» oder ziehe eine .exe herein.",
 "New game":"Neues Spiel","Name":"Name","Path to exe":"Pfad zur .exe","Browse":"Durchsuchen…","Scan folder":"Ordner scannen",
 "Preset":"Profil","Own prefix":"Eigenes Präfix (empfohlen für AAA)","Arguments":"Argumente","Add":"Hinzufügen",
 "Settings":"Einstellungen","Work dir":"Arbeitsordner","Virtual desktop":"Virtueller Desktop (leer = aus)","Save":"Speichern",
 "Game folder":"Spieleordner","Prefix":"Präfix","Remove":"Entfernen",
 "GameMode":"GameMode (CPU/IO-Priorität)","MangoHUD":"MangoHUD (FPS-Overlay)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"DXVK-HUD","Wine debug":"Wine-Debuglog","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (Runner für schwierige Spiele)","Download latest":"Neueste herunterladen",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Prüfen","Update pm":"Aktualisieren (Paketmanager)",
 "Governor":"CPU-Governor (Performance = weniger FPS-Einbrüche)","Enable Perf":"Performance aktivieren",
 "Swappiness":"Swappiness (10 = weniger Ruckler)","Set 10":"Auf 10 setzen","GameMode daemon":"GameMode-Daemon",
 "Enable":"Aktivieren","Shader cache":"Shader-Cache (nach DXVK-Wechsel leeren)","Clear":"Leeren",
 "Optimization title":"Systemoptimierung","Install all":"Alles automatisch installieren",
 "Check system":"System prüfen","Setup desc":"Einmalig: System-Stack (Wine, DXVK, Vulkan-Treiber).",
 "Logs title":"Logs — Spiel wählen:","No log":"Noch kein Log — starte das Spiel.",
 "Launched":"Gestartet","Log":"Log","Not starting":"Startet nicht? Öffne 📋 Logs.",
 "Language":"Sprache","Theme":"Theme",
},
"fr": {
 "Library":"Bibliothèque","Updates":"Mises à jour","Optimization":"Optimisation","Setup":"Installation","Logs":"Journaux",
 "My games":"Mes jeux","Add game":"Ajouter un jeu","Refresh":"Actualiser","Fix & Launch":"Réparer et lancer","Launch":"Lancer",
 "Drop hint":"Glisse-dépose un .exe ou un dossier de jeu ici",
 "Empty":"Vide. Clique sur «+ Ajouter» ou glisse un .exe.",
 "New game":"Nouveau jeu","Name":"Nom","Path to exe":"Chemin du .exe","Browse":"Parcourir…","Scan folder":"Analyser le dossier",
 "Preset":"Profil","Own prefix":"Préfixe dédié (recommandé pour AAA)","Arguments":"Arguments","Add":"Ajouter",
 "Settings":"Paramètres","Work dir":"Dossier de travail","Virtual desktop":"Bureau virtuel (vide = désactivé)","Save":"Enregistrer",
 "Game folder":"Dossier du jeu","Prefix":"Préfixe","Remove":"Supprimer",
 "GameMode":"GameMode (priorité CPU/IO)","MangoHUD":"MangoHUD (superposition FPS)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"HUD DXVK","Wine debug":"Journal debug Wine","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (runner pour jeux difficiles)","Download latest":"Télécharger la dernière version",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Vérifier","Update pm":"Mettre à jour (gestionnaire)",
 "Governor":"Gouverneur CPU (performance = moins de baisses de FPS)","Enable Perf":"Activer Performance",
 "Swappiness":"Swappiness (10 = moins de saccades)","Set 10":"Régler à 10","GameMode daemon":"Démon GameMode",
 "Enable":"Activer","Shader cache":"Cache de shaders (vider après changement DXVK)","Clear":"Vider",
 "Optimization title":"Optimisation système","Install all":"Tout installer automatiquement",
 "Check system":"Vérifier le système","Setup desc":"Une fois : pile système (Wine, DXVK, pilotes Vulkan).",
 "Logs title":"Journaux — choisis un jeu :","No log":"Pas encore de journal — lance le jeu.",
 "Launched":"Lancé","Log":"Journal","Not starting":"Ne démarre pas ? Ouvre 📋 les journaux.",
 "Language":"Langue","Theme":"Thème",
},
"es": {
 "Library":"Biblioteca","Updates":"Actualizaciones","Optimization":"Optimización","Setup":"Instalación","Logs":"Registros",
 "My games":"Mis juegos","Add game":"Añadir juego","Refresh":"Actualizar","Fix & Launch":"Reparar y lanzar","Launch":"Lanzar",
 "Drop hint":"Arrastra un .exe o una carpeta de juego aquí",
 "Empty":"Vacío. Pulsa «+ Añadir» o arrastra un .exe.",
 "New game":"Nuevo juego","Name":"Nombre","Path to exe":"Ruta del .exe","Browse":"Examinar…","Scan folder":"Escanear carpeta",
 "Preset":"Perfil","Own prefix":"Prefijo propio (recomendado para AAA)","Arguments":"Argumentos","Add":"Añadir",
 "Settings":"Ajustes","Work dir":"Carpeta de trabajo","Virtual desktop":"Escritorio virtual (vacío = desactivado)","Save":"Guardar",
 "Game folder":"Carpeta del juego","Prefix":"Prefijo","Remove":"Eliminar",
 "GameMode":"GameMode (prioridad CPU/IO)","MangoHUD":"MangoHUD (overlay FPS)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"HUD de DXVK","Wine debug":"Registro debug de Wine","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (runner para juegos difíciles)","Download latest":"Descargar última",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Comprobar","Update pm":"Actualizar (gestor de paquetes)",
 "Governor":"Gobernador CPU (performance = menos caídas de FPS)","Enable Perf":"Activar Performance",
 "Swappiness":"Swappiness (10 = menos tirones)","Set 10":"Poner en 10","GameMode daemon":"Demonio GameMode",
 "Enable":"Activar","Shader cache":"Caché de shaders (limpiar al cambiar DXVK)","Clear":"Limpiar",
 "Optimization title":"Optimización del sistema","Install all":"Instalar todo automáticamente",
 "Check system":"Comprobar sistema","Setup desc":"Una vez: pila del sistema (Wine, DXVK, drivers Vulkan).",
 "Logs title":"Registros — elige un juego:","No log":"Aún no hay registro — lanza el juego.",
 "Launched":"Lanzado","Log":"Registro","Not starting":"¿No arranca? Abre 📋 registros.",
 "Language":"Idioma","Theme":"Tema",
},
"pt": {
 "Library":"Biblioteca","Updates":"Atualizações","Optimization":"Otimização","Setup":"Instalação","Logs":"Registros",
 "My games":"Meus jogos","Add game":"Adicionar jogo","Refresh":"Atualizar","Fix & Launch":"Reparar e iniciar","Launch":"Iniciar",
 "Drop hint":"Arraste um .exe ou pasta de jogo para cá",
 "Empty":"Vazio. Clique em «+ Adicionar» ou arraste um .exe.",
 "New game":"Novo jogo","Name":"Nome","Path to exe":"Caminho do .exe","Browse":"Procurar…","Scan folder":"Escanear pasta",
 "Preset":"Perfil","Own prefix":"Prefixo próprio (recomendado para AAA)","Arguments":"Argumentos","Add":"Adicionar",
 "Settings":"Ajustes","Work dir":"Pasta de trabalho","Virtual desktop":"Desktop virtual (vazio = desligado)","Save":"Salvar",
 "Game folder":"Pasta do jogo","Prefix":"Prefixo","Remove":"Remover",
 "GameMode":"GameMode (prioridade CPU/IO)","MangoHUD":"MangoHUD (overlay FPS)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"HUD do DXVK","Wine debug":"Log de debug do Wine","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (runner para jogos difíceis)","Download latest":"Baixar mais recente",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Verificar","Update pm":"Atualizar (gerenciador)",
 "Governor":"Governador CPU (performance = menos quedas de FPS)","Enable Perf":"Ativar Performance",
 "Swappiness":"Swappiness (10 = menos travadas)","Set 10":"Definir 10","GameMode daemon":"Daemon GameMode",
 "Enable":"Ativar","Shader cache":"Cache de shaders (limpar ao trocar DXVK)","Clear":"Limpar",
 "Optimization title":"Otimização do sistema","Install all":"Instalar tudo automaticamente",
 "Check system":"Verificar sistema","Setup desc":"Uma vez: stack do sistema (Wine, DXVK, drivers Vulkan).",
 "Logs title":"Registros — escolha um jogo:","No log":"Sem registro ainda — inicie o jogo.",
 "Launched":"Iniciado","Log":"Registro","Not starting":"Não inicia? Abra 📋 registros.",
 "Language":"Idioma","Theme":"Tema",
},
"uk": {
 "Library":"Бібліотека","Updates":"Оновлення","Optimization":"Оптимізація","Setup":"Встановлення","Logs":"Логи",
 "My games":"Мої ігри","Add game":"Додати гру","Refresh":"Оновити","Fix & Launch":"Полагодити й запустити","Launch":"Запуск",
 "Drop hint":"Перетягни .exe або папку з грою сюди",
 "Empty":"Порожньо. Натисни «＋ Додати» або перетягни .exe.",
 "New game":"Нова гра","Name":"Назва","Path to exe":"Шлях до .exe","Browse":"Огляд…","Scan folder":"Сканувати папку",
 "Preset":"Пресет","Own prefix":"Окремий префікс (рекомендовано для AAA)","Arguments":"Аргументи","Add":"Додати",
 "Settings":"Налаштування","Work dir":"Робоча папка","Virtual desktop":"Віртуальний робочий стіл (порожньо = вимк)","Save":"Зберегти",
 "Game folder":"Папка гри","Prefix":"Префікс","Remove":"Видалити",
 "GameMode":"GameMode (пріоритет CPU/IO)","MangoHUD":"MangoHUD (оверлей FPS)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"DXVK HUD","Wine debug":"Wine debug-лог","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (раннер для складних ігор)","Download latest":"Завантажити останній",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Перевірити","Update pm":"Оновити (пакетний менеджер)",
 "Governor":"CPU governor (performance — менше просідань FPS)","Enable Perf":"Увімкнути Performance",
 "Swappiness":"Swappiness (10 — менше фрізів)","Set 10":"Встановити 10","GameMode daemon":"GameMode (демон)",
 "Enable":"Увімкнути","Shader cache":"Кеш шейдерів (чистити після зміни DXVK)","Clear":"Очистити",
 "Optimization title":"Оптимізація системи","Install all":"Встановити все автоматично",
 "Check system":"Перевірити систему","Setup desc":"Один раз: системний стек (Wine, DXVK, Vulkan-драйвери).",
 "Logs title":"Логи — обери гру:","No log":"Лога ще нема — запусти гру.",
 "Launched":"Запущено","Log":"Лог","Not starting":"Не запускається? Відкрий 📋 логи.",
 "Language":"Мова","Theme":"Тема",
},
"pl": {
 "Library":"Biblioteka","Updates":"Aktualizacje","Optimization":"Optymalizacja","Setup":"Instalacja","Logs":"Logi",
 "My games":"Moje gry","Add game":"Dodaj grę","Refresh":"Odśwież","Fix & Launch":"Napraw i uruchom","Launch":"Uruchom",
 "Drop hint":"Przeciągnij .exe lub folder gry tutaj",
 "Empty":"Pusto. Kliknij «+ Dodaj» lub przeciągnij .exe.",
 "New game":"Nowa gra","Name":"Nazwa","Path to exe":"Ścieżka do .exe","Browse":"Przeglądaj…","Scan folder":"Skanuj folder",
 "Preset":"Profil","Own prefix":"Osobny prefiks (zalecane dla AAA)","Arguments":"Argumenty","Add":"Dodaj",
 "Settings":"Ustawienia","Work dir":"Folder roboczy","Virtual desktop":"Wirtualny pulpit (pusto = wył)","Save":"Zapisz",
 "Game folder":"Folder gry","Prefix":"Prefiks","Remove":"Usuń",
 "GameMode":"GameMode (priorytet CPU/IO)","MangoHUD":"MangoHUD (nakładka FPS)","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"HUD DXVK","Wine debug":"Log debug Wine","LAA":"Large Address Aware",
 "GEProton":"GE-Proton (runner dla trudnych gier)","Download latest":"Pobierz najnowszy",
 "DXVK card":"DXVK + VKD3D-Proton (DirectX → Vulkan)","Check":"Sprawdź","Update pm":"Aktualizuj (menedżer pakietów)",
 "Governor":"Governor CPU (performance = mniej spadków FPS)","Enable Perf":"Włącz Performance",
 "Swappiness":"Swappiness (10 = mniej przycięć)","Set 10":"Ustaw 10","GameMode daemon":"Demon GameMode",
 "Enable":"Włącz","Shader cache":"Pamięć shaderów (czyść po zmianie DXVK)","Clear":"Wyczyść",
 "Optimization title":"Optymalizacja systemu","Install all":"Zainstaluj wszystko automatycznie",
 "Check system":"Sprawdź system","Setup desc":"Raz: stos systemowy (Wine, DXVK, sterowniki Vulkan).",
 "Logs title":"Logi — wybierz grę:","No log":"Brak loga — uruchom grę.",
 "Launched":"Uruchomiono","Log":"Log","Not starting":"Nie startuje? Otwórz 📋 logi.",
 "Language":"Język","Theme":"Motyw",
},
"zh": {
 "Library":"游戏库","Updates":"更新","Optimization":"优化","Setup":"安装","Logs":"日志",
 "My games":"我的游戏","Add game":"添加游戏","Refresh":"刷新","Fix & Launch":"修复并启动","Launch":"启动",
 "Drop hint":"将 .exe 或游戏文件夹拖到这里",
 "Empty":"空空如也。点击「＋ 添加」或拖入 .exe。",
 "New game":"新游戏","Name":"名称","Path to exe":".exe 路径","Browse":"浏览…","Scan folder":"扫描文件夹",
 "Preset":"预设","Own prefix":"独立前缀（AAA 游戏推荐）","Arguments":"参数","Add":"添加",
 "Settings":"设置","Work dir":"工作目录","Virtual desktop":"虚拟桌面（留空=关闭）","Save":"保存",
 "Game folder":"游戏文件夹","Prefix":"前缀","Remove":"删除",
 "GameMode":"GameMode（CPU/IO 优先级）","MangoHUD":"MangoHUD（FPS 覆盖层）","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"DXVK HUD","Wine debug":"Wine 调试日志","LAA":"Large Address Aware",
 "GEProton":"GE-Proton（困难游戏运行器）","Download latest":"下载最新版",
 "DXVK card":"DXVK + VKD3D-Proton（DirectX → Vulkan）","Check":"检查","Update pm":"更新（包管理器）",
 "Governor":"CPU 调度器（performance = 减少掉帧）","Enable Perf":"启用 Performance",
 "Swappiness":"Swappiness（10 = 减少卡顿）","Set 10":"设为 10","GameMode daemon":"GameMode 守护进程",
 "Enable":"启用","Shader cache":"着色器缓存（更换 DXVK 后清理）","Clear":"清理",
 "Optimization title":"系统优化","Install all":"全自动安装",
 "Check system":"检查系统","Setup desc":"一次性安装系统组件（Wine、DXVK、Vulkan 驱动）。",
 "Logs title":"日志 — 选择游戏：","No log":"暂无日志 — 启动游戏。",
 "Launched":"已启动","Log":"日志","Not starting":"无法启动？打开 📋 日志。",
 "Language":"语言","Theme":"主题",
},
"ja": {
 "Library":"ライブラリ","Updates":"アップデート","Optimization":"最適化","Setup":"セットアップ","Logs":"ログ",
 "My games":"マイゲーム","Add game":"ゲームを追加","Refresh":"更新","Fix & Launch":"修復して起動","Launch":"起動",
 "Drop hint":".exe またはゲームフォルダをここにドラッグ",
 "Empty":"空です。「＋ 追加」をクリックするか .exe をドラッグしてください。",
 "New game":"新しいゲーム","Name":"名前","Path to exe":".exe のパス","Browse":"参照…","Scan folder":"フォルダをスキャン",
 "Preset":"プリセット","Own prefix":"専用プレフィックス（AAA 向け推奨）","Arguments":"引数","Add":"追加",
 "Settings":"設定","Work dir":"作業ディレクトリ","Virtual desktop":"仮想デスクトップ（空欄=オフ）","Save":"保存",
 "Game folder":"ゲームフォルダ","Prefix":"プレフィックス","Remove":"削除",
 "GameMode":"GameMode（CPU/IO 優先度）","MangoHUD":"MangoHUD（FPS オーバーレイ）","Fsync":"Fsync","Esync":"Esync",
 "DXVK HUD":"DXVK HUD","Wine debug":"Wine デバッグログ","LAA":"Large Address Aware",
 "GEProton":"GE-Proton（難しいゲーム向けランナー）","Download latest":"最新版をダウンロード",
 "DXVK card":"DXVK + VKD3D-Proton（DirectX → Vulkan）","Check":"チェック","Update pm":"更新（パッケージマネージャー）",
 "Governor":"CPU ガバナー（performance = FPS 低下を軽減）","Enable Perf":"Performance を有効化",
 "Swappiness":"Swappiness（10 = カクつき低減）","Set 10":"10 に設定","GameMode daemon":"GameMode デーモン",
 "Enable":"有効化","Shader cache":"シェーダーキャッシュ（DXVK 変更後にクリア）","Clear":"クリア",
 "Optimization title":"システム最適化","Install all":"すべて自動インストール",
 "Check system":"システムをチェック","Setup desc":"一度だけ：システムスタック（Wine、DXVK、Vulkan ドライバー）。",
 "Logs title":"ログ — ゲームを選択：","No log":"ログはまだありません — ゲームを起動してください。",
 "Launched":"起動しました","Log":"ログ","Not starting":"起動しない？📋 ログを開く。",
 "Language":"言語","Theme":"テーマ",
},
}

_current = "ru"


def _load():
    global _current
    try:
        if CONFIG.exists():
            _current = json.loads(CONFIG.read_text(encoding="utf-8")).get("lang", "ru")
    except Exception:
        pass


def save(key, value):
    ensure_dirs()
    cfg = {}
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    cfg[key] = value
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def tr(key: str) -> str:
    """EN: translate key -> current language (fallback: en -> key)."""
    return T.get(_current, {}).get(key) or T["en"].get(key, key)


def set_lang(code: str):
    global _current
    if code in LANGS:
        _current = code
        save("lang", code)


def current():
    return _current


_load()
