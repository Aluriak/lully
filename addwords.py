
import sys
import random
import itertools
import argparse

from cdctools.words import NOUNS, ADJECTIVES



nouns = set(NOUNS)
adjs = set(ADJECTIVES)
kind = 'n'

def get_all_words(kind: str) -> set[str]:
    return set(nouns if kind == 'n' else adjs)

def set_all_words(words: set[str], kind: str):
    global nouns, adjs
    if kind == 'n':
        nouns = words
    else:
        adjs = words

def save_words(fout: str = 'cdctools/words.py'):
    with open(fout, 'w') as fd:
        fd.write('NOUNS = (\n')
        fd.write(''.join(f"    {repr(w)},\n" for w in sorted(list(nouns))))
        fd.write(')\n\n')
        fd.write('ADJECTIVES = (\n')
        fd.write(''.join(f"    {repr(w)},\n" for w in sorted(list(adjs))))
        fd.write(')\n')
    print(f"File {fout} written with {len(nouns)} nouns and {len(adjs)} adjectives")

while True:
    added, existing = 0, 0
    for new in input('Adjectif: ' if kind == 'a' else 'Nom: ').split():
        new = new.title().strip()
        words = get_all_words(kind=kind)

        if new.lower() in {'a', 'n'}:
            kind = new.lower()
            words = get_all_words(kind=kind)

        elif new.startswith('-'):
            new = new[1:].title()
            print(f'Remove {new} from {kind}…')
            if new in words:
                words.remove(new)
                set_all_words(words, kind=kind)
            else:
                print("Did not exists")

        elif new in words:
            print(f'{new} is already present in {kind}')
            existing += 1

        elif new:  # new is not in words
            words.add(new)
            set_all_words(words, kind=kind)
            print(f'{new} added to {kind}')
            added += 1
    print(f'Added: {added} \t Existing: {existing}')
    save_words()







def add_group():
    kind, *words_lists = map(str.lower, sys.argv[1:])
    words = [w for w in set(itertools.chain.from_iterable(
        map(str.title, map(str.strip, words.split(',')))
        for words in words_lists
    )) if w]

    print(f"{len(words)} input words of kind {kind}.")

    if kind in {'a', 'adj', 'adjective', 'adjectives'}:
        kind = 'a'
    elif kind in {'n', 'noun', 'nouns', 'noun', 'nom'}:
        kind = 'n'
    else:
        print(f"Invalid {kind=}")
        exit(1)



    EXISTING = set(NOUNS if kind == 'n' else ADJECTIVES)
    WORDS = set(words)
    WHOLE = EXISTING | WORDS
    NEW = WHOLE - EXISTING
    NOTNEW = WORDS - NEW


    print(f"Type : {'noms' if kind == 'n' else 'adjectifs'}")
    print(f"Nouveaux mots : {len(NEW)} ({', '.join(NEW)})")
    print(f"Déjà présents : {len(NOTNEW)} (eg {', '.join(random.sample(list(NOTNEW), min(10, len(NOTNEW))))})")
    print(f"Total : {len(WHOLE)}")

    with open('out.py', 'w') as fd:
        fd.write(('NOUNS' if kind == 'n' else 'ADJECTIVES') + ' = (\n')
        fd.write(''.join(f"    {repr(w)},\n" for w in sorted(list(WHOLE))))
        fd.write(')\n')
    print(f"File out.py written with all {kind}.")
