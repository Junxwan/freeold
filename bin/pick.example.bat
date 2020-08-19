:: 專案venv path
CALL <project path>\venv\Scripts\activate

:: 模式
set /p model=model:

:: 日期
set /p date=date:

:: 資料來源目錄
set /p dataDir=dataDir:

:: 輸出
set /p output=output:

:: 專案目錄
cd /d <project path>

:: venv python path
<project path>\venv\Scripts\python pick.py -model=%model% -date=%date% -dataDir=%dataDir% -output=%output%

pause

