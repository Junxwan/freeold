:: 專案venv path
CALL <project path>\venv\Scripts\activate

:: 模式
set /p model=model:

:: 輸入的execl path
set /p input=input:

:: 輸出的目錄
set /p output=output:

:: 專案目錄
cd /d <project path>

:: venv python path
<project path>\venv\Scripts\python execl.py -model=%model% -input=%input% -output=%output%

pause

