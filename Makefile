APP_NAME     := zapusk
ENTRY        := src/$(APP_NAME)
BUILD_DIR    := build

ICON_SRC     := assets/$(APP_NAME).svg
DESKTOP_SRC  := assets/$(APP_NAME).desktop

PREFIX       := $(HOME)/.local
BIN_DIR      := $(PREFIX)/bin
APP_DIR      := $(PREFIX)/share/applications
ICON_DIR     := $(PREFIX)/share/icons/hicolor/scalable/apps

VENV_BIN     := .venv/bin
PYTHON       := $(if $(wildcard $(VENV_BIN)/python),$(VENV_BIN)/python,python3)

DIST_NAME    := $(basename $(notdir $(ENTRY))).dist
BIN_PATH     := $(BUILD_DIR)/$(DIST_NAME)/$(APP_NAME)
ONEFILE_PATH := $(BUILD_DIR)/$(APP_NAME)

NUITKA_FLAGS := \
	--enable-plugin=pyside6       \
	--include-package-data=zapusk \
	--output-dir=$(BUILD_DIR)     \
	--output-filename=$(APP_NAME) \
	--assume-yes-for-downloads    \
	--show-progress

.DEFAULT_GOAL := build

.PHONY: build standalone onefile run install uninstall clean

build: onefile

onefile:
	$(PYTHON) -m nuitka --standalone --onefile $(NUITKA_FLAGS) $(ENTRY)
	chmod +x $(ONEFILE_PATH)

standalone:
	$(PYTHON) -m nuitka --standalone $(NUITKA_FLAGS) $(ENTRY)
	chmod +x $(BIN_PATH)

run: standalone
	./$(BIN_PATH)

install: build
	mkdir -p $(BIN_DIR) $(APP_DIR) $(ICON_DIR)
	install -m 755 $(ONEFILE_PATH) $(BIN_DIR)/$(APP_NAME)
	install -m 644 $(DESKTOP_SRC) $(APP_DIR)/$(APP_NAME).desktop
	@if [ -f "$(ICON_SRC)" ]; then \
		install -m 644 $(ICON_SRC) $(ICON_DIR)/$(APP_NAME).svg; \
	fi
	-update-desktop-database $(APP_DIR) 2>/dev/null || true
	-gtk-update-icon-cache -f -t $(PREFIX)/share/icons/hicolor 2>/dev/null || true
	@echo ">>> Installed to $(BIN_DIR)/$(APP_NAME)"

uninstall:
	rm -f $(BIN_DIR)/$(APP_NAME)
	rm -f $(APP_DIR)/$(APP_NAME).desktop
	rm -f $(ICON_DIR)/$(APP_NAME).svg
	-update-desktop-database $(APP_DIR) 2>/dev/null || true
	@echo ">>> $(APP_NAME) uninstallled"

clean:
	rm -rf $(BUILD_DIR)
