"""Helpers around SQL language"""
from typing import Iterable



def named_tables_in(sql: str) -> Iterable[str]:
    """

    >>> list(named_tables_in("SELECT a, b FROM ta JOIN tb"))
    ['ta', 'tb']

    """
    import sqlglot
    parsed = sqlglot.parse_one(sql)
    for source in parsed.find_all(sqlglot.expressions.Table):
        if str(source).isidentifier():  # cora_doc is ok, read_parquet('s3://...') is not
            yield source.name
