"""stats.py - survival and effect-size helpers used by the API (same maths as scripts/analyze.py)."""
import math
import numpy as np
from scipy import stats as st


def km(durations, removed):
    """Kaplan-Meier curve. durations: lifetimes; removed: 1 = removal observed, 0 = censored.
    Returns list of [t, S(t), at_risk] points (step function, starts at [0, 1])."""
    t = np.asarray(durations, float)
    e = np.asarray(removed, int)
    if len(t) == 0:
        return []
    order = np.argsort(t, kind="stable")
    t, e = t[order], e[order]
    pts, s, n = [[0.0, 1.0, int(len(t))]], 1.0, len(t)
    for ut in np.unique(t):
        mask = t == ut
        d = int(e[mask].sum())
        if d:
            s *= 1 - d / n
            pts.append([float(ut), round(s, 5), int(n)])
        n -= int(mask.sum())
    tmax = float(t.max())
    if pts[-1][0] < tmax:
        pts.append([tmax, pts[-1][1], int(n)])
    return pts


def km_median(pts):
    for t, s, _ in pts:
        if s <= 0.5:
            return t
    return None


def logrank(t1, e1, t2, e2):
    t = np.concatenate([t1, t2]).astype(float)
    e = np.concatenate([e1, e2]).astype(int)
    g = np.concatenate([np.zeros(len(t1)), np.ones(len(t2))])
    O1 = E1 = V = 0.0
    for ut in np.unique(t[e == 1]):
        r = t >= ut
        n, n1 = r.sum(), (r & (g == 0)).sum()
        d = ((t == ut) & (e == 1)).sum()
        O1 += ((t == ut) & (e == 1) & (g == 0)).sum()
        E1 += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    if V == 0:
        return None, None
    chi = (O1 - E1) ** 2 / V
    return round(float(chi), 3), round(float(1 - st.chi2.cdf(chi, 1)), 4)


def cliffs_delta(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if not len(a) or not len(b):
        return None
    gt = sum(int((x > b).sum()) for x in a)
    lt = sum(int((x < b).sum()) for x in a)
    return round((gt - lt) / (len(a) * len(b)), 3)


def clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v
