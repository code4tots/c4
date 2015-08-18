# C4

Just as Coffeescript is 'just javascript', C4 is 'just C'.

That is, the language is designed in such a way that the C that is generated is more or less obvious, while adding some syntactic sugar.

C4 IS NOT a superset of C. The expression syntax is a bit simplified, and syntax of many other constructs (e.g. struct, function definitions and includes) are a bit different to make parsing easier.

### Usage

See sampletest.bat or sampletest.sh

The gist of it is, once you have written your program in say, my_program.c4,

You can get the C version by running

	python -m c4 my_program.c4 > my_program.c

In the future, I may support generating separate header and source files. It's not implemented yet because I don't really need it yet.

If you are on 64 bit Windows environment and have Visual Studio 15 installed, you can run

	sampletest.bat

to see sample.c4 run.

Actually you could probably also double click on sampletest.bat and it would have the same effect.
