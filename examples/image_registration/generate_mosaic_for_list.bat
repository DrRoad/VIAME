@echo off

REM Setup VIAME Paths (no need to set if installed to registry or already set up)

SET VIAME_INSTALL=.\..\..
SET INPUT_IMAGE_PATTERN=C:\path\to\some\images\*.png

CALL "%VIAME_INSTALL%\setup_viame.bat"

REM Run Pipeline

dir /s/b "%INPUT_IMAGE_PATTERN%" > input_list.txt

kwiver.exe runner "%VIAME_INSTALL%/configs/pipelines/register_using_homographies.pipe" ^
                  -s input:video_filename=input_list.txt

python.exe create_mosaic.py first_mosaic.png output-homog.txt "%INPUT_IMAGE_PATTERN%" --step 1
