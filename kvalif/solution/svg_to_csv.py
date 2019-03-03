#!/usr/bin/env python3

import sys
import xml.etree.ElementTree
import re
import csv


def main(ifn, ofn):
    root = xml.etree.ElementTree.parse(ifn).getroot()

    nodes = {}

    for node in root.iter():
        if node.tag.endswith('circle'):
            match = re.search(r'fill:#(......)', node.attrib['style'] \
                              if 'style' in node.attrib else 'fill:#000000')
            color = match.group(1)
            nodes[color] = nodes.get(color, []) + [(
                (int(node.attrib['cx']), int(node.attrib['cy']))
            )]

    with open(ofn, 'w') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for color, items in nodes.items():
            for node in items:
                writer.writerow(['node', node[0], node[1], color])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: svg_to_csv.py input.svg output.csv\n')
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
