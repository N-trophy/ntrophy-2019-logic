#!/usr/bin/env python3

import csv
import sys


def main(ifn, ofn):
    with open(ifn) as csvfile:
        reader = csv.reader(csvfile)
        points = []
        for row in reader:
            if row and row[0] == 'node':
                points.append((int(row[1]), int(row[2])))


    with open(ofn, 'w') as svg:
        svg.write('<svg width="100%" height="100%" '
                  'xmlns="http://www.w3.org/2000/svg" '
                  'xmlns:xlink= "http://www.w3.org/1999/xlink">\n')
        for x, y in points:
            svg.write('\t<circle cx="%d" cy="%d" r="10" />\n' % (x, y))
        svg.write("\n</svg>\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: svgen.py filename.csv output.svg\n')
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
