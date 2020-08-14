set path=C:\Users\hugh8\Desktop\research\data\tick
set file=D:\free\code.xlsx
set /p date=date:
set /p ck=ck:
set /p session=session:

cd D:\free

C:\Users\hugh8\AppData\Local\Programs\Python\Python39\Python tick.py -ck=%ck% -session=%session% -date=%date% -dir=%path% -file=%file%

pause