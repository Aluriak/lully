""""""

import uuid
import argparse
from collections import Counter

from . import hashing


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)

    ss = subs.add_parser('id', description='id')
    ss.add_argument('n', type=int, default=30, help="number of id to yield")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_cli()

    if args.action == 'id':
        codes = []
        for _ in range(args.n):
            code = hashing.human_code(uuid.uuid4())
            # print(code)
            codes.append(code)
        stats = Counter(codes)
        print(stats.most_common(10))
        for duplicata, count in sorted(Counter(stats.values()).items(), key=lambda d: d[0]):
            print(f"{duplicata} × {count}")
