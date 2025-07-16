# mypy: ignore-errors

FRENCH_STOPWORDS = [  # taken from nltk.corpus.stopwords.words('french')
    'au', 'aux', 'avec', 'ce', 'ces', 'dans', 'de', 'des', 'du', 'elle', 'en', 'et', 'eux', 'il', 'ils', 'je', 'la', 'le', 'les', 'leur', 'lui', 'ma', 'mais', 'me', 'même', 'mes', 'moi', 'mon', 'ne', 'nos', 'notre', 'nous', 'on', 'ou', 'par', 'pas', 'pour', 'qu', 'que', 'qui', 'sa', 'se', 'ses', 'son', 'sur', 'ta', 'te', 'tes', 'toi', 'ton', 'tu', 'un', 'une', 'vos', 'votre', 'vous', 'c', 'd', 'j', 'l', 'à', 'm', 'n', 's', 't', 'y', 'été', 'étée', 'étées', 'étés', 'étant', 'étante', 'étants', 'étantes', 'suis', 'es', 'est', 'sommes', 'êtes', 'sont', 'serai', 'seras', 'sera', 'serons', 'serez', 'seront', 'serais', 'serait', 'serions', 'seriez', 'seraient', 'étais', 'était', 'étions', 'étiez', 'étaient', 'fus', 'fut', 'fûmes', 'fûtes', 'furent', 'sois', 'soit', 'soyons', 'soyez', 'soient', 'fusse', 'fusses', 'fût', 'fussions', 'fussiez', 'fussent', 'ayant', 'ayante', 'ayantes', 'ayants', 'eu', 'eue', 'eues', 'eus', 'ai', 'as', 'avons', 'avez', 'ont', 'aurai', 'auras', 'aura', 'aurons', 'aurez', 'auront', 'aurais', 'aurait', 'aurions', 'auriez', 'auraient', 'avais', 'avait', 'avions', 'aviez', 'avaient', 'eut', 'eûmes', 'eûtes', 'eurent', 'aie', 'aies', 'ait', 'ayons', 'ayez', 'aient', 'eusse', 'eusses', 'eût', 'eussions', 'eussiez', 'eussent'
]


def get_edsnlp(mots_cles, df):
    import pandas as pd
    import edsnlp
    import edsnlp.pipes as eds
    print(type(df))

    regex = dict(label=f'{mots_cles}')
    nlp = edsnlp.blank('eds')
    nlp.add_pipe(
    eds.matcher(
        regex=regex,
        attr='LOWER',
        ),
    )
    nlp.add_pipe(eds.sentences())
    nlp.add_pipe(eds.negation())
    nlp.add_pipe(eds.hypothesis())
    nlp.add_pipe(eds.family())


    dataframes = []

    for index, x in df.iterrows():
        doc = nlp(df['TEXTE'][index])
        for ent in doc.ents:
            d = dict(
                ipp=df['IPP'][index],
                timestamp =df['TIMESTAMP'][index],
                source_id = df['SOURCE_ID'][index],
                lexical_variant=ent.text,
                negation=ent._.negation,
                hypothesis=ent._.hypothesis,
                family=ent._.family,
            )
            dataframes.append(d)
    dataframes = pd.DataFrame(dataframes)
    dataframes = dataframes.drop_duplicates()

    return dataframes
