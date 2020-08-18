CALL D:\free\venv\Scripts\activate

set /p input=input:
set /p output=output:

cd /d D:\free

D:\free\venv\Scripts\python execl.py -model=cmoney-weak-day -input=%input% -output=%output%

pause

