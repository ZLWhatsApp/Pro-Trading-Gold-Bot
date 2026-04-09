name: Trading Bot Runner

on:
  push:
    branches: [ main ]
  workflow_dispatch: # هذا السطر يتيح لك تشغيله يدوياً بضغطة زر

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install pyTelegramBotAPI
      - name: Run Bot
        run: python main.py
