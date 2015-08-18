python -m c4 sample.c4 > sample.c && \
gcc -Wall -Werror -Wpedantic --std=c89 sample.c && \
./a.out && \
rm -f a.out sample.c
