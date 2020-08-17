:: 專案venv path
CALL <project path>\venv\Scripts\activate

:: 保存圖檔目錄
set dir=<save image file path>

:: 總計有多少自選股
set /p total=total:

:: 專案目錄
cd /d <project path>

:: venv python path
<project path>\venv\Scripts\python auto.py -total=%total% -model=day -dir=%dir%

pause