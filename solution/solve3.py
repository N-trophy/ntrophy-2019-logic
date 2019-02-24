#!/usr/bin/env python3

import csv
import sys


def mindist(points):
    xx, yy = zip(*points)
    return (sum(xx)/len(xx), sum(yy)/len(yy))


def main(filename):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        points = []
        for row in reader:
            if row and row[0] == 'node':
                points.append((int(row[1]), int(row[2])))

    print(mindist(points))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: solve3.py filename.csv\n')
        sys.exit(1)

    main(sys.argv[1])
