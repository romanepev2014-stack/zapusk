#!/usr/bin/env bash
# EN: Quick launcher — starts the Zapusk GUI.
# RU: Быстрый запуск — открывает GUI Zapusk.
cd "$(dirname "$0")"
exec python -m zapusk gui
