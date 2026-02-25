""""""

import uuid
import argparse
import itertools
from collections import Counter, defaultdict
from typing import Union, Iterable

from . import hashing, words, vgauge

import bisect



def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)

    ss = subs.add_parser('test-id', description='testing id generation')
    ss.add_argument('n', type=int, default=0, help="number of id to yield (0 for combination count)")
    ss = subs.add_parser('id', description='id generation from input')
    ss.add_argument('value', type=str, help="string to yield id from")

    return parser.parse_args()


def na2na(na: str) -> Iterable[str]:
    return na.split(' ')

def show_elements_repartition(stats: Union[Iterable[str], dict[str, int]], elements: list[str] = sorted('ABCDEFGHIJKLMNOPQRSTUVWXYZÂÇÉÈÊÎŒ'), elem_to_elems = lambda x: [x], elem_to_key = lambda x: x[0], keep_count_on = lambda c: c>0, header: bool = True, leading: str = ''):
    counts_per_elem = {l: 0 for l in elements}
    if not isinstance(stats, dict):
        stats = {v: 1 for v in stats}
    for elems, count in stats.items():
        if keep_count_on(count):
            for elem in elem_to_elems(elems):
                counts_per_elem[elem_to_key(elem)] += count
    max_counts = max(counts_per_elem.values())
    #print(f"{counts_per_elem=}, {max_counts=} total_count={sum(counts_per_elem.values())}")
    try:
        gauges = {l: vgauge(counts_per_elem[l] / max_counts) for l in sorted(counts_per_elem)}
    except ZeroDivisionError:
        gauges = {l: '.' for l in sorted(counts_per_elem)}

    if header:
        ret = ' '*len(leading) + ''.join(str(v) for v in gauges.keys()) + '\n'
    else:
        ret = ''
    print( ret + leading + ''.join(str(v) for v in gauges.values()) )

def produce_codes(nb_loop: int, use_uuid:bool = True, **kwargs):
    codes = []
    progress_bar = None
    for idx in range(nb_loop):
        code = hashing.human_code(uuid.uuid4() if use_uuid else idx, **kwargs)
        # print(code)
        codes.append(code)
        if progress_bar != round(idx / nb_loop * 100):
            progress_bar = round(idx / nb_loop * 100)
            print('\r[' + ('█'*progress_bar).ljust(100), ']', end='', sep='', flush=True)
    print()
    return codes


if __name__ == '__main__':
    args = parse_cli()

    if args.action == 'id':
        print(hashing.human_code(args.value))

    if args.action == 'test-id':
        nb_comb = len(words.NOUNS) * len(words.ADJECTIVES)
        print(f"{len(words.NOUNS)} nouns × {len(words.ADJECTIVES)} adjectives = {nb_comb} combinations\n")
        nb_loop = int(args.n or nb_comb)
        stats = {}
        for exp, (arg_uuid, arg_sum) in enumerate(itertools.product((True, False), repeat=2), start=1):
            print(f"\nExperiment {exp} use uuid={arg_uuid} sum={arg_sum}")
            codes = produce_codes(nb_loop, use_uuid=arg_uuid, method_sum=arg_sum)
            s = stats[exp] = Counter(codes)
            print(s.most_common(10))
            total_count = sum(s.values())
            nb_per_duplicata = Counter(s.values())
            for duplicata, count in sorted(nb_per_duplicata.items(), key=lambda d: d[0]):
                print('\t'+f"{duplicata} × {count}".ljust(14), f"{round(count/total_count*100,3)}% du total")
            total_duplicata = sum(c for d, c in nb_per_duplicata.items() if d>1)
            print(f"Collision : {round(total_duplicata/total_count*100,3)}%")

        print()
        show_elements_repartition(words.NOUNS,      leading='     nouns: ')
        show_elements_repartition(words.ADJECTIVES, leading='adjectives: ', header=False)
        for exp, expstats in stats.items():
            show_elements_repartition(expstats,     leading= f'EXP{exp}: '.ljust(len('adjectives: ')), header=False, keep_count_on=lambda c: c>0, elem_to_elems=na2na)

        print(
            "Cette expérience démontre que la méthode sum introduit un biais important dans les données.\n"
            "La somme sur les bytes va effectivement créer une gaussienne dans la répartition des entiers générés, et donc un biais de sur-représentation de certains indexes.\n"
            "La conséquence pratique est l'augmentation du nombre de collisions."
        )
