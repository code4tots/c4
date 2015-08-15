@echo off
cl || "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
python c4.py > sample.c && cl sample.c && sample && del sample.*
