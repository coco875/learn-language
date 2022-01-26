@echo off
pyinstaller --onefile --noconsole main.py
cp -r language dist
cp -r vocabulary dist
cp config.json dist
zip -r app.zip dist