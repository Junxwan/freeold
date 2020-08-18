:: 專案venv path
CALL <project path>\venv\Scripts\activate

:: 保存tick資料path
set path=<tick data path>

:: 個股代碼xlsx
set file=<code xlsx>

:: tick日期
set /p date=date:

:: cmoney api ck
set /p ck=ck:

:: cmoney cookie session
set /p session=session:

:: 專案目錄
cd /d <project path>

:: venv python path
<project path>\venv\Scripts\python crawler.py -cmCk=%ck% -cmSession=%session% -cmDate=%date% -dir=%path% -file=%file%

pause