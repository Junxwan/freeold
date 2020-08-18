CALL D:\free\venv\Scripts\activate

set path=C:\Users\hugh8\Desktop\research\data\tick
set file=D:\free\code.xlsx
set /p date=date:
set /p ck=ck:
set /p session=session:

cd /d D:\free

D:\free\venv\Scripts\python data.py -ck=%ck% -session=%session% -date=%date% -dir=%path% -file=%file%

pause