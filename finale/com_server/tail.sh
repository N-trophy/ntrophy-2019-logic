#/bin/bash

tail -f 2000_stdout.txt | sed 's/^/2000: /' &
tail -f 2001_stdout.txt | sed 's/^/2001: /' &
tail -f 2002_stdout.txt | sed 's/^/2002: /' &
tail -f 2003_stdout.txt | sed 's/^/2003: /' &
