import bisect
from scipy.stats import hypergeom


def hypergeometric_test(pop: int, in_pop: int, sample: int, in_sample: int) -> float:
    """
    pop       -- population totale
    in_pop    -- sous-ensemble valide de la population
    sample    -- taille de l'échantillon
    in_sample -- sous-ensemble valide de l'échantillon
    """
    # p-value one-tailed (enrichissement)
    p_value = hypergeom.sf(in_sample - 1, pop, in_pop, sample)
    # ou : 1 - hypergeom.cdf(k - 1, M, n, N)
    return p_value

def hypergeometric_test_diagnostic(pop: int, in_pop: int, sample: int, in_sample: int) -> dict:
    p = hypergeometric_test(pop, in_pop, sample, in_sample)

    if p > 0.05:
        return {}
    return {
        'p': float(p),
        'enrichment': bool(p < 0.05),
        'valid': in_pop <= pop and sample <= pop and in_sample <= sample,
    }

def basic_pvalue_significance(p: float) -> str:
    SIGNIFICANCE_THRESHOLD = {
        .001: '+++',
        .01: '++',
        .05: '+',
        .1: '--',
        1: '---',
    }
    assert p >= 0, f"p-value cannot be negative, found {p}"
    assert p <= 1, f"p-value cannot exceed 1, found {p}"
    return next(v for k, v in SIGNIFICANCE_THRESHOLD.items() if p <= k)


def hypergeometric_test_diagnostic(pop: int, in_pop: int, sample: int, in_sample: int, *, get_significance: callable = basic_pvalue_significance) -> dict:
    valid = in_pop <= pop and sample <= pop and in_sample <= sample and in_sample >= 0

    # Espérance et variance sous H0
    expected = sample * (in_pop / pop) if pop > 0 else 0
    variance = (
        expected * (1 - in_pop / pop) * (pop - sample) / (pop - 1)
        if pop > 1 else 0
    )

    # Fold enrichment : ratio observé / attendu
    fold_enrichment = in_sample / expected if expected > 0 else float("inf")

    # Direction
    direction = "enriched" if in_sample > expected else ("depleted" if in_sample < expected else "stable")

    # p-value
    # if enriched:
    p = float(hypergeometric_test(pop, in_pop, sample, in_sample))
    # else:
        # # sous-représentation : P(X <= in_sample)
        # p = float(hypergeom.cdf(in_sample, pop, in_pop, sample))

    return {
        "valid": valid,
        "p": p,
        "significance": get_significance(p),
        "direction": direction,
        "fold_enrichment": round(fold_enrichment, 4),
        "observed": in_sample,
        "expected": round(expected, 4),
        "expected_variance": round(variance, 4),
    }
