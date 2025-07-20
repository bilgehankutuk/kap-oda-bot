#!/bin/bash
echo "== Installing Chromium via Playwright =="
playwright install chromium
echo "== Starting Flask app =="
python main.py
