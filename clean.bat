@echo off

:: Set the base path here
set "base_path_log=C:\Users\patrick\PycharmProjects\LogicMaster_Evaluation"

:: Folders to clean (relative to the base path)
set folders=("logs" "logs\preprocessing" "logs\ai\ddpg" "logs\ai\ppo" "logs\ai\qlearning" "resources\models\qlearning" "resources\models\ppo" "resources\models\ddpg")

:: Iterate through each folder and delete its files
for %%f in %folders% do (
    set "folder_path=%base_path%\%%~f"

    if exist "%%~f" (
        echo Cleaning folder: %%~f
        del /q "%%~f\*.*"
        echo Folder %%~f cleaned.
    ) else (
        echo Folder does not exist: %%~f
    )
)
