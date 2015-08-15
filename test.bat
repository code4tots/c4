cl || "C:\Program Files\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"

python c4.py > sample.c && \
cl sample.c && \
a.out && \
del sample.c sample.obj
