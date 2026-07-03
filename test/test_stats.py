from lully import stats

def test_hyperg():
    # La somme des pmf vaut 1
    assert abs(sum(stats.hypergeometric_test_exact(20, 7, 12, k) for k in range(8)) - 1) < 1e-12
    # Enrichissement maximal : P(X >= 7) == P(X = 7), pas 0
    assert stats.hypergeometric_test(20, 7, 12, 7) == stats.hypergeometric_test_exact(20, 7, 12, 7)
    # Déplétion totale : P(X <= 0) == P(X = 0)
    assert stats.hypergeometric_test(20, 7, 12, 0) == stats.hypergeometric_test_exact(20, 7, 12, 0)
