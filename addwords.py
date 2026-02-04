
import sys
import random
import itertools
import argparse

import lully as ll
from rich import print as printr



KINDCOLOR = {'a': 'bold blue', 'n': 'bold green'}
KINDNAME = {'a': 'Adjectif', 'n': 'Nom', 'b': 'Nom+Adjectif'}
WORDS = {'a': set(ll.ADJECTIVES), 'n': set(ll.NOUNS)}
cur_kind = 'n'

#cli_input=input(KINDNAME[kind]+': ')
def get_words_per_kind(cli_input: list[str]) -> dict[str, set[str]]:
    global cur_kind
    words_per_kind = {k: [] for k in KINDNAME}
    for w in cli_input:
        if not w.strip(): continue
        if w in KINDNAME:
            cur_kind = w
        else:
            words_per_kind[cur_kind].append(w)
    return collapse_b_kind(words_per_kind)

def collapse_b_kind(w_per_k: dict[str, list[str]]) -> dict[str, set[str]]:
    if w_per_k['b']:
        for one, two in ll.chunks(w_per_k['b'], n=2):
            w_per_k['n'].append(one)
            w_per_k['a'].append(two)
    return {'n': set(w_per_k['n']), 'a': set(w_per_k['a'])}


def save_words(fout: str = 'lully/words.py'):
    with open(fout, 'w') as fd:
        fd.write('NOUNS = (\n')
        fd.write(''.join(f"    {repr(w)},\n" for w in sorted(list(WORDS['n']))))
        fd.write(')\n\n')
        fd.write('ADJECTIVES = (\n')
        fd.write(''.join(f"    {repr(w)},\n" for w in sorted(list(WORDS['a']))))
        fd.write(')\n')
    printr(f"File {fout} written with {len(WORDS['n'])} [{KINDCOLOR['n']}]nouns[/{KINDCOLOR['n']}] and {len(WORDS['a'])} [{KINDCOLOR['a']}]adjectives[/{KINDCOLOR['a']}]")


while True:
    added, existing = 0, 0
    try:
        news = get_words_per_kind(input(KINDNAME[cur_kind]+': ').split())
    except (KeyboardInterrupt, EOFError):
        break
    # print('NEWS:', news)
    for kind in news:
        for new in news[kind]:
            new = new.title().strip()

            if new.startswith('-'):
                new = new[1:].title()  # remove the leading dash
                print(f'Remove {new} from {kind}… ', end='', flush=True)
                if new in WORDS[kind]:
                    WORDS[kind].remove(new)
                    print("Done")
                else:
                    print("Did not exists")

            elif new in WORDS[kind]:
                print(f'{new} is already present in {kind}')
                existing += 1

            elif new:  # new is not in words
                WORDS[kind].add(new)
                printr(f'[{KINDCOLOR[kind]}]{new}[/{KINDCOLOR[kind]}] added to {kind}')
                added += 1
    print(f'Added: {added} \t Existing: {existing}')
    save_words()
