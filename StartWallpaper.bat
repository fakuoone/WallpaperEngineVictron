@ECHO OFF
B:
Start "" steam://rungameid/431960
timeout /T 15 /nobreak >null
taskkill /IM steam.exe /F /T
taskkill /IM steamwebhelper.exe /F /T 
taskkill /IM ui32.exe
cd webserver_directory
@python main.py
