@echo off
cl || "C:\Program Files\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
python c4.py > sample.c && cl sample.c && sample && del sample.*
