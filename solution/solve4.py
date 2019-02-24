#!/usr/bin/env python3

import csv
import sys


def mindist(points):
    xx, yy = zip(*points)
    return (sum(xx)/len(xx), sum(yy)/len(yy))


def main(filename):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        points = {}
        for row in reader:
            if row and row[0] == 'node':
                color = row[3]
                points[color] = points.get(color, []) + [(int(row[1]), int(row[2]))]

    for color, nodes in points.items():
        x, y = mindist(nodes)
        print('%.2f,%.2f' % (x, y))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: solve4.py filename.csv\n')
        sys.exit(1)

    main(sys.argv[1])
