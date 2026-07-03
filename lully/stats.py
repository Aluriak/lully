"""High level function for hypergeometric test.

See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.hypergeom.html
for explanations and more functions

"""
from scipy.stats import hypergeom
from typing import Callable


def hypergeometric_test(pop: int, in_pop: int, sample: int, in_sample: int) -> float:
    """
    pop       -- population totale
    in_pop    -- sous-ensemble valide de la population
    sample    -- taille de l'échantillon
    in_sample -- sous-ensemble valide de l'échantillon

    Renvoie la probabilité P(X≤in_sample) d'obtenir in-sample ou moins (si déplétion),
    ou P(X≥in_sample) d'obtenir in-sample ou plus (si enrichissement).

    Pour avoir P(X=in_sample), cf hypergeometric_test_exact
    """
    expected = sample * (in_pop / pop) if pop > 0 else 0
    if in_sample < expected:  # déplétion : P(X <= k)
        return float(hypergeom.cdf(in_sample, pop, in_pop, sample))
    # enrichissement : P(X >= k)
    return float(hypergeom.sf(in_sample - 1, pop, in_pop, sample))

def hypergeometric_test_exact(pop: int, in_pop: int, sample: int, in_sample: int) -> float:
    """
    pop       -- population totale
    in_pop    -- sous-ensemble valide de la population
    sample    -- taille de l'échantillon
    in_sample -- sous-ensemble valide de l'échantillon

    Renvoie la probabilité P(X=in_sample)
    """
    return float(hypergeom.pmf(in_sample, pop, in_pop, sample))


def basic_pvalue_significance(p: float) -> str:
    SIGNIFICANCE_THRESHOLD = {
        .001: '+++',
        .01: '++',
        .05: '+',
        .1: '-',
        .2: '--',
        float('inf'): '---',
    }
    assert p >= 0, f"p-value cannot be negative, found {p}"
    assert p <= 1, f"p-value cannot exceed 1, found {p}"
    return next(v for k, v in SIGNIFICANCE_THRESHOLD.items() if p <= k)


def hypergeometric_test_diagnostic(pop: int, in_pop: int, sample: int, in_sample: int, *, get_significance: Callable[[float], str] = basic_pvalue_significance) -> dict:
    valid = (
        0 <= in_pop <= pop  # sous-population ⊆ population
        and 0 <= sample <= pop  # échantillon ⊆ population
        # upper : pas plus de succès que l'échantillon ou la sous-population
        # lower : les non-membres (pop - in_pop) ne suffisent pas toujours à remplir l'échantillon
        and max(0, sample - (pop - in_pop)) <= in_sample <= min(sample, in_pop)
    )
    if not valid:
        return {"valid": False}

    # Espérance et variance sous H0
    expected = sample * (in_pop / pop) if pop > 0 else 0
    variance = (expected * (1 - in_pop / pop) * (pop - sample) / (pop - 1)) if pop > 1 else 0

    # Fold enrichment : ratio observé / attendu
    fold_enrichment = in_sample / expected if expected > 0 else float("inf")

    direction = "enriched" if in_sample > expected else ("depleted" if in_sample < expected else "stable")
    p = hypergeometric_test(pop, in_pop, sample, in_sample)

    return {
        "valid": valid,
        "p": p,
        "p_exact": hypergeometric_test_exact(pop, in_pop, sample, in_sample),
        "significance": get_significance(p),
        "direction": direction,
        "fold_enrichment": round(fold_enrichment, 4),
        "observed": in_sample,
        "expected": round(expected, 4),
        "expected_variance": round(variance, 4),
    }
