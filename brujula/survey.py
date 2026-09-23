"""Stratified ultimate-cluster estimates with explicit publication controls.

The caller supplies the complete responding/resident design frame, before
restricting age, geography, education or outcome. Final survey weights are
treated as fixed; no unobserved calibration or finite-population correction
is inferred. A singleton stratum fails by default; the explicit
``singleton_policy="adjust"`` option applies the project's full-frame PSU
grand-mean approximation. This module does not establish source or universe
validity.
"""

from __future__ import annotations

import math

import numpy as np

Z90 = 1.6448536269514722
VARIANCE_METHOD = "taylor_ultimate_cluster_wr_final_weights_v1"


class SurveyDesign:
    """Reusable full-frame design with an explicit singleton policy.

    True singleton strata fail at construction by default. With
    ``singleton_policy="adjust"``, variance centers singleton PSU totals on
    the grand mean across all full-frame PSUs and uses a singleton correction
    factor of one. Adjusted estimates are marked ``REVIEW`` and expose a
    precision note because this is a project approximation, not an official
    INEGI treatment.

    ``allow_zero_weights`` acknowledges a caller-owned audit; zero-weight rows
    never count as sample support. A design stratum/PSU must retain positive
    weight support. No data, weights or IDs are mutated by this class.
    """

    def __init__(self, weights, strata, psu, *, allow_zero_weights=False, singleton_policy="fail"):
        if singleton_policy not in {"fail", "adjust"}:
            raise ValueError("singleton_policy must be fail or adjust")
        self.singleton_policy = singleton_policy
        self.weights = np.array(weights, dtype=float, copy=True)
        if self.weights.ndim != 1 or not self.weights.size:
            raise ValueError("weights must be a nonempty one-dimensional array")
        if not np.isfinite(self.weights).all() or (self.weights < 0).any():
            raise ValueError("weights must be finite and nonnegative")
        self.zero_weight_count = int(np.count_nonzero(self.weights == 0))
        if self.zero_weight_count and not allow_zero_weights:
            raise ValueError("zero weights require explicit caller audit")
        stratum_ids = self._ids(strata, "strata")
        psu_ids = self._ids(psu, "psu")
        _, stratum_index = np.unique(stratum_ids, return_inverse=True)
        _, psu_index = np.unique(psu_ids, return_inverse=True)
        pairs = np.column_stack((stratum_index, psu_index))
        clusters, self._cluster_index = np.unique(pairs, axis=0, return_inverse=True)
        self._cluster_strata = clusters[:, 0]
        self._cluster_count = len(clusters)
        cluster_weights = np.bincount(self._cluster_index, weights=self.weights,
                                      minlength=self._cluster_count)
        if (cluster_weights <= 0).any() or not np.isfinite(cluster_weights).all():
            raise ValueError("each design PSU requires finite positive weight support")
        self._stratum_counts = np.bincount(self._cluster_strata)
        self.singleton_strata_count = int(np.count_nonzero(self._stratum_counts == 1))
        if self.singleton_strata_count and singleton_policy == "fail":
            raise ValueError("full design has a singleton stratum; official treatment required")
        self.n_strata_design = len(self._stratum_counts)
        self.design_df = self._cluster_count - self.n_strata_design
        self.weights.setflags(write=False)

    def _ids(self, values, name):
        array = np.asarray(values, dtype=object)
        if array.ndim != 1 or len(array) != len(self.weights):
            raise ValueError(f"{name} must match the full design frame")
        result = []
        for value in array:
            if isinstance(value, (bool, np.bool_)) or not isinstance(value, (str, int, np.integer)):
                raise ValueError(f"{name} IDs must be nonempty strings or integers")
            text = str(value)
            if not text.strip():
                raise ValueError(f"{name} IDs cannot be empty")
            result.append(text)
        return np.asarray(result)

    def _mask(self, domain):
        if domain is None:
            return np.ones(len(self.weights), dtype=bool)
        mask = np.asarray(domain)
        if mask.dtype.kind != "b" or mask.shape != self.weights.shape:
            raise ValueError("domain must be a boolean mask matching the full frame")
        return mask

    def _values(self, values, domain, name):
        array = np.asarray(values, dtype=float)
        if array.shape != self.weights.shape:
            raise ValueError(f"{name} must match the full design frame")
        if not np.isfinite(array[domain]).all():
            raise ValueError(f"{name} must be finite inside the domain")
        # Mask before multiplication: NaN outside a domain must not contaminate it.
        return np.where(domain, array, 0.0)

    def _variance(self, influence):
        if not np.isfinite(influence).all():
            raise ValueError("nonfinite weighted contribution")
        totals = np.bincount(self._cluster_index, weights=influence,
                             minlength=self._cluster_count)
        sums = np.bincount(self._cluster_strata, weights=totals,
                           minlength=self.n_strata_design)
        means = sums / self._stratum_counts
        differences = totals - means[self._cluster_strata]
        singleton = self._stratum_counts == 1
        # Explicit project approximation matching R survey lonely.psu="adjust":
        # a singleton is centered on the grand mean of full-frame PSU totals.
        # Do not treat it as certainty, collapse strata, or filter domain PSUs.
        if self.singleton_strata_count:
            means[singleton] = totals.sum() / self._cluster_count
            differences = totals - means[self._cluster_strata]
        corrections = np.divide(self._stratum_counts, self._stratum_counts - 1,
                                out=np.ones(self.n_strata_design), where=~singleton)
        variance = float(np.sum(differences ** 2 * corrections[self._cluster_strata]))
        if not math.isfinite(variance):
            raise ValueError("nonfinite design variance")
        return variance

    def _result(self, estimate, variance, support, weighted_denominator, *, proportion=False):
        n = int(np.count_nonzero(support))
        psus = int(len(np.unique(self._cluster_index[support])))
        se = math.sqrt(variance) if variance is not None else None
        cv = 100 * se / abs(estimate) if estimate not in (None, 0) else None
        boundary = proportion and estimate is not None and estimate in (0.0, 100.0)
        lower = upper = None
        ci_method = "logit_delta_normal_90" if proportion else "normal_wald_90"
        if estimate is not None and se is not None and not boundary:
            if proportion:
                p = estimate / 100
                logit = math.log(p) - math.log1p(-p)
                logit_se = (se / 100) / (p * (1 - p))

                def expit(value):
                    if value >= 0:
                        return 1 / (1 + math.exp(-value))
                    exp_value = math.exp(value)
                    return exp_value / (1 + exp_value)

                lower = 100 * expit(logit - Z90 * logit_se)
                upper = 100 * expit(logit + Z90 * logit_se)
            else:
                lower, upper = estimate - Z90 * se, estimate + Z90 * se
        reasons = []
        if estimate is None:
            reasons.append("zero_denominator")
        if n < 30:
            reasons.append("sample_size_below_30")
        if psus < 2:
            reasons.append("fewer_than_two_domain_psus")
        if boundary:
            reasons.append("proportion_boundary")
        if se == 0:
            reasons.append("zero_variance")
        if estimate == 0 and se is not None and se > 0:
            reasons.append("undefined_cv_at_zero")
        if cv is not None and cv >= 30:
            reasons.append("cv_at_least_30")
        if estimate is None or n < 30 or psus < 2:
            status = "UNKNOWN"
        elif reasons or (cv is not None and cv >= 15) or self.singleton_strata_count:
            status = "REVIEW"
        else:
            status = "MEASURED"
        return {
            "estimate": estimate,
            "value": None if reasons else estimate,
            "standard_error": se,
            "coefficient_variation": cv,
            "ci_lower": lower,
            "ci_upper": upper,
            "confidence_level": 0.90,
            "ci_method": ci_method,
            "variance_method": VARIANCE_METHOD + ("_singleton_adjust" if self.singleton_policy == "adjust" else ""),
            "singleton_policy": self.singleton_policy,
            "singleton_strata_count": self.singleton_strata_count,
            "precision_note": "Project variance approximation; not official INEGI precision." if self.singleton_strata_count else None,
            "design_df": self.design_df,
            "n_psu_domain": psus,
            "n_strata_design": self.n_strata_design,
            "sample_size": n,
            "weighted_denominator": weighted_denominator,
            "status": status,
            "suppression_reason": ";".join(reasons) if reasons else None,
            "zero_weight_count": self.zero_weight_count,
        }

    def total(self, values, domain=None):
        """Estimate a total; sample support counts nonzero domain contributors."""
        mask = self._mask(domain)
        values = self._values(values, mask, "values")
        contributions = self.weights * values
        estimate = float(contributions.sum())
        if not math.isfinite(estimate):
            raise ValueError("nonfinite total")
        support = mask & (values != 0) & (self.weights > 0)
        return self._result(estimate, self._variance(contributions), support,
                            float(self.weights[mask].sum()))

    def ratio(self, numerator, denominator, domain=None, *, percent=False):
        """Estimate a ratio, counting positive denominator rows as sample support.

        For percentages require 0 <= numerator <= denominator. Zero denominator
        rows must also have zero numerator. Missing outcomes must be excluded by
        the caller's explicit boolean domain, never filled with an observed zero.
        """
        mask = self._mask(domain)
        num = self._values(numerator, mask, "numerator")
        den = self._values(denominator, mask, "denominator")
        if (den < 0).any() or ((den == 0) & (num != 0)).any():
            raise ValueError("denominator must be nonnegative; zero requires zero numerator")
        if percent and ((num < 0).any() or (num > den).any()):
            raise ValueError("proportions require 0 <= numerator <= denominator")
        support = mask & (den > 0) & (self.weights > 0)
        weighted_den = float(np.dot(self.weights, den))
        weighted_num = float(np.dot(self.weights, num))
        if not math.isfinite(weighted_den) or not math.isfinite(weighted_num):
            raise ValueError("nonfinite weighted ratio components")
        if weighted_den == 0:
            return self._result(None, None, support, 0.0, proportion=percent)
        ratio = weighted_num / weighted_den
        if not math.isfinite(ratio):
            raise ValueError("nonfinite ratio")
        influence = self.weights * (num - ratio * den) / weighted_den
        scale = 100.0 if percent else 1.0
        return self._result(ratio * scale, self._variance(influence) * scale ** 2,
                            support, weighted_den, proportion=percent)
