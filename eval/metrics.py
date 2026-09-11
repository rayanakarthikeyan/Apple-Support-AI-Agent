import math, re
from typing import List, Dict, Any, Tuple
from collections import Counter

def compute_classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    total = len(y_true)
    if total == 0:
        return {'accuracy': 0.0, 'macro_f1': 0.0}
    accuracy = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / total
    classes = sorted(list(set(y_true) | set(y_pred)))
    f1s = []
    class_metrics = {}
    for c in classes:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp == c)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != c and yp == c)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp != c)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        f1s.append(f1)
        class_metrics[c] = {'precision': round(prec, 4), 'recall': round(rec, 4), 'f1': round(f1, 4), 'support': sum(1 for yt in y_true if yt == c)}
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    return {'accuracy': round(accuracy, 4), 'macro_f1': round(macro_f1, 4), 'per_class': class_metrics}

def compute_binary_metrics(y_true: List[bool], y_pred: List[bool]) -> Dict[str, Any]:
    total = len(y_true)
    if total == 0:
        return {}
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt is True and yp is True)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt is False and yp is True)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt is True and yp is False)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt is False and yp is False)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    acc = (tp + tn) / total
    far = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {'accuracy': round(acc, 4), 'precision': round(prec, 4), 'recall': round(rec, 4), 'f1': round(f1, 4), 'false_alarm_rate': round(far, 4), 'confusion': {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn}}

def compute_token_f1_and_rouge(hypothesis: str, reference: str) -> Dict[str, float]:
    hyp_tokens = re.findall(r'[a-z0-9]+', hypothesis.lower())
    ref_tokens = re.findall(r'[a-z0-9]+', reference.lower())
    if not hyp_tokens or not ref_tokens:
        return {'token_f1': 0.0, 'rouge_l': 0.0}
    common = Counter(hyp_tokens) & Counter(ref_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return {'token_f1': 0.0, 'rouge_l': 0.0}
    prec = num_same / len(hyp_tokens)
    rec = num_same / len(ref_tokens)
    token_f1 = (2 * prec * rec) / (prec + rec)
    m, n = len(hyp_tokens), len(ref_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if hyp_tokens[i] == ref_tokens[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])
    lcs = dp[m][n]
    rl_prec = lcs / m
    rl_rec = lcs / n
    rouge_l = (2 * rl_prec * rl_rec) / (rl_prec + rl_rec) if (rl_prec + rl_rec) > 0 else 0.0
    return {'token_f1': round(token_f1, 4), 'rouge_l': round(rouge_l, 4)}

def compute_cohens_kappa(rater_a: List[int], rater_b: List[int]) -> float:
    if len(rater_a) != len(rater_b) or not rater_a:
        return 0.0
    n = len(rater_a)
    categories = sorted(list(set(rater_a) | set(rater_b)))
    po = sum(1 for a, b in zip(rater_a, rater_b) if a == b) / n
    pe = 0.0
    for cat in categories:
        pa = sum(1 for a in rater_a if a == cat) / n
        pb = sum(1 for b in rater_b if b == cat) / n
        pe += pa * pb
    if pe == 1.0:
        return 1.0
    kappa = (po - pe) / (1.0 - pe)
    return round(kappa, 4)
