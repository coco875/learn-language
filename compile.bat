@echo off
C:\Users\Corentin\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\pyinstaller.exe --onefile --noconsole main.py
cp -r language dist
cp -r vocabulary dist
cp config.json dist
zip -r app.zip dist