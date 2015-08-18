@echo off
cl || call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
python -m c4 sample.c4 > sample.c && cl sample.c && sample.exe
del /q sample.c sample.exe sample.obj
