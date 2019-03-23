#!/bin/bash

python3 -u com_server.py 2000.txt 2000 > 2000_stdout.txt &
python3 -u com_server.py 2001.txt 2001 > 2001_stdout.txt &
python3 -u com_server.py 2002.txt 2002 > 2002_stdout.txt &
python3 -u com_server.py 2003.txt 2003 > 2003_stdout.txt &
