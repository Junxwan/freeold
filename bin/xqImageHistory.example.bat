:: 專案venv path
CALL <project path>\venv\Scripts\activate

:: 保存圖檔目錄
set dir=<save image file path>

:: 總計有多少自選股
set /p total=total:

:: 技術分析前進幾天
set /p prevDay=prevDay:

:: 走勢圖前進幾月
set /p prevMonth=prevMonth:

:: 走勢圖日期X
set /p dayX=dayX:

:: 走勢圖日期Y
set /p dayY=dayY:

:: 專案目錄
cd /d <project path>

:: venv python path
<project path>\venv\Scripts\python auto.py -total=%total% -model=history -dir=%dir% -prevDay=%prevDay% -prevMonth=%prevMonth% -dayX=%dayX% -dayY=%dayY%

pause