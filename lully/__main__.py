""""""

import uuid
import argparse
from collections import Counter, defaultdict

from . import hashing, words, vgauge

import bisect



def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)

    ss = subs.add_parser('id', description='id')
    ss.add_argument('n', type=int, default=0, help="number of id to yield (0 for combination count)")

    return parser.parse_args()


def na2na(na: str) -> tuple[str, str]:
    return na.split(' ')

def show_elements_repartition(stats: dict[str, int], elements: list[str] = sorted('ABCDEFGHIJKLMNOPQRSTUVWXYZÂÇÉÈÊÎŒ'), elem_to_elems = lambda x: [x], elem_to_key = lambda x: x[0], keep_count_on = lambda c: c>0, header: bool = True, leading: str = ''):
        counts_per_elem = {l: 0 for l in elements}
        if not isinstance(stats, dict):
            stats = {v: 1 for v in stats}
        for elems, count in stats.items():
            if keep_count_on(count):
                for elem in elem_to_elems(elems):
                    counts_per_elem[elem_to_key(elem)] += count
        max_counts = max(counts_per_elem.values())
        #print(f"{counts_per_elem=}, {max_counts=} total_count={sum(counts_per_elem.values())}")
        counts_per_elem = {l: vgauge(counts_per_elem[l] / max_counts) for l in sorted(counts_per_elem)}
        if header:
            ret = ' '*len(leading) + ''.join(str(v) for v in counts_per_elem.keys()) + '\n'
        else:
            ret = ''
        print( ret + leading + ''.join(str(v) for v in counts_per_elem.values()) )


if __name__ == '__main__':
    args = parse_cli()

    if args.action == 'id':
        nb_comb = len(words.NOUNS) * len(words.ADJECTIVES)
        print(f"{len(words.NOUNS)} nouns × {len(words.ADJECTIVES)} adjectives = {nb_comb} combinations\n")
        codes = []
        nb_loop = int(args.n or nb_comb)
        progress_bar = None
        for idx in range(nb_loop):
            code = hashing.human_code(uuid.uuid4())
            # print(code)
            codes.append(code)
            if progress_bar != round(idx / nb_loop * 100):
                progress_bar = round(idx / nb_loop * 100)
                print('\r[' + ('█'*progress_bar).ljust(100), ']', end='', sep='', flush=True)
        print()
        stats = Counter(codes)
        print(stats.most_common(10))
        total_count = sum(stats.values())
        for duplicata, count in sorted(Counter(stats.values()).items(), key=lambda d: d[0]):
            print(f"{duplicata} × {count}".ljust(14), f"{round(count/total_count*100,3)}% du total")

        print()
        show_elements_repartition(words.NOUNS,      leading='     nouns: ')
        show_elements_repartition(words.ADJECTIVES, leading='adjectives: ', header=False)
        show_elements_repartition(stats,            leading='duplicates: ', header=False, keep_count_on=lambda c: c>1, elem_to_elems=na2na)

