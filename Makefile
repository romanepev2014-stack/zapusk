APP_NAME  := zapusk
ENTRY     := src/zapusk
BUILD_DIR := build
VENV_BIN  := .venv/bin
PYTHON    := $(if $(wildcard $(VENV_BIN)/python),$(VENV_BIN)/python,python3)

DIST_NAME    := $(basename $(notdir $(ENTRY))).dist
BIN_PATH     := $(BUILD_DIR)/$(DIST_NAME)/$(APP_NAME)
ONEFILE_PATH := $(BUILD_DIR)/$(APP_NAME)

NUITKA_FLAGS := \
	--enable-plugin=pyside6 \
	--output-dir=$(BUILD_DIR) \
	--output-filename=$(APP_NAME) \
	--assume-yes-for-downloads \
	--show-progress

.DEFAULT_GOAL := build

.PHONY: build standalone onefile run clean

build: onefile

onefile:
	$(PYTHON) -m nuitka --standalone --onefile $(NUITKA_FLAGS) $(ENTRY)
	chmod +x $(ONEFILE_PATH)

standalone:
	$(PYTHON) -m nuitka --standalone $(NUITKA_FLAGS) $(ENTRY)
	chmod +x $(BIN_PATH)

run: standalone
	./$(BIN_PATH)

clean:
	rm -rf $(BUILD_DIR)
