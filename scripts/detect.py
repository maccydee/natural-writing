#!/usr/bin/env python3
"""Slop detector — a dependency-free self-test for the natural-writing skill.

Run it on a draft to get an objective report of the machine-tells the skill
cares about, so you know exactly what to fix before looping again:

    python3 detect.py path/to/draft.md
    python3 detect.py --text "paste some prose here"

It uses ONLY the Python standard library, so it runs anywhere. It does NOT
prove a text is or isn't AI — it flags the concrete patterns that push prose
toward "machine-written," each tied to a fixable location. Lower score = more
human-sounding. Exit code is 0 if the draft passes the bar, 1 if it needs work.

Optional, only if `transformers`+`torch` happen to be installed:
    python3 detect.py draft.md --perplexity
adds GPT-2 perplexity/burstiness (the signal classic detectors use). Skip it
if the libraries aren't present — the core report stands on its own.
"""
import sys, re, json, argparse, math

# ---- vocabulary (kept in sync with references/ai-tells.md) ----
TELL_WORDS = [
    "delve", "underscore", "boasts", "showcase", "leverage", "foster", "garner",
    "robust", "crucial", "pivotal", "vibrant", "meticulous", "seamless",
    "comprehensive", "nuanced", "multifaceted", "enhance", "bolster", "utilize",
    "facilitate", "endeavor", "myriad", "plethora", "tapestry", "landscape",
    "realm", "mosaic", "ecosystem", "symphony", "labyrinth", "beacon",
    "cornerstone", "bedrock", "testament", "kaleidoscope", "odyssey",
    "game-changer", "game changer", "elevate", "unlock", "harness", "navigate",
    "curated", "artisanal", "bespoke",
]
THROAT_CLEARING = [
    r"in today'?s (?:fast-paced |digital |modern )?(?:world|landscape|age|era)",
    r"in the (?:ever-)?(?:evolving|changing) (?:world|landscape) of",
    r"it'?s (?:important|worth) (?:to note|noting) that",
    r"when it comes to\b",
    r"this (?:article|post|guide|piece) will (?:explore|discuss|cover|delve)",
]
HEDGES = ["often", "typically", "generally", "usually", "arguably", "perhaps",
          "somewhat", "relatively", "in some cases", "may", "might", "can be",
          "tends to", "some would argue", "it could be said"]
VAGUE_ATTRIB = [r"studies (?:show|have shown|suggest)", r"experts (?:say|agree|believe)",
                r"research(?:ers)? (?:show|say|suggest|indicate)", r"many (?:people )?believe",
                r"it is (?:widely )?(?:known|believed|understood)", r"scientists (?:say|believe)"]

def words(t): return re.findall(r"\b[\w'-]+\b", t)
def sentences(t):
    t = re.sub(r"\s+", " ", t.strip())
    return [s for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]

def find_all(patterns, t, flags=re.I):
    hits = []
    for p in patterns:
        for m in re.finditer(p, t, flags):
            hits.append(m.group(0))
    return hits

def stdev(xs):
    if len(xs) < 2: return 0.0
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5

def analyze(text):
    wl = words(text)
    wc = max(1, len(wl))
    sents = sentences(text)
    slens = [len(words(s)) for s in sents]
    per1k = 1000.0 / wc

    checks = []  # (name, severity, count, detail, points)  severity: FAIL/WARN/OK

    # 1. tell-words
    tw = [w for w in wl if w.lower() in TELL_WORDS]
    tw += [h for h in ["game changer", "game-changer"] if h in text.lower()]
    dens = len(tw) * per1k
    sev = "FAIL" if dens > 4 else ("WARN" if dens > 1.5 else "OK")
    checks.append(("tell-words", sev, len(tw), (", ".join(sorted(set(w.lower() for w in tw))[:8]) or "none"),
                   min(30, len(tw) * 4)))

    # 2. throat-clearing openers/transitions
    tc = find_all(THROAT_CLEARING, text)
    sev = "FAIL" if tc else "OK"
    checks.append(("throat-clearing", sev, len(tc), (", ".join(tc[:4]) or "none"), len(tc) * 12))

    # 3. signature constructions
    not_only = len(re.findall(r"not only\b.{0,60}?\bbut also\b", text, re.I | re.S))
    neg_pivot = len(re.findall(r"\b(it'?s|its)\s+not\s+(just\s+)?[^.,;]{1,40}[.,;]\s*(it'?s|its)\b", text, re.I))
    whether = len(re.findall(r"whether you'?re\b[^.]{0,40}\bor\b", text, re.I))
    sig = not_only + neg_pivot + whether
    sev = "FAIL" if sig else "OK"
    detail = []
    if not_only: detail.append(f"'not only...but also' x{not_only}")
    if neg_pivot: detail.append(f"'it's not X, it's Y' x{neg_pivot}")
    if whether: detail.append(f"'whether you're...or' x{whether}")
    checks.append(("signature-constructions", sev, sig, (", ".join(detail) or "none"), sig * 15))

    # 4. sentence-length burstiness (low variance = machine-like)
    sd = stdev(slens)
    cv = sd / (sum(slens) / len(slens)) if slens else 0
    sev = "FAIL" if cv < 0.35 else ("WARN" if cv < 0.5 else "OK")
    checks.append(("rhythm-burstiness", sev, round(cv, 2),
                   f"stdev={sd:.1f}, cv={cv:.2f} (want cv>=0.5; higher=more varied)",
                   (20 if cv < 0.35 else (8 if cv < 0.5 else 0))))

    # 5. over-correction: too many ultra-short sentences (fragments as a NEW tell)
    frag = sum(1 for L in slens if L <= 3)
    frag_ratio = frag / len(slens) if slens else 0
    sev = "WARN" if frag_ratio > 0.25 else "OK"
    checks.append(("fragment-overuse", sev, frag,
                   f"{frag}/{len(slens)} sentences <=3 words ({frag_ratio:.0%}); overuse reads as engineered",
                   (10 if frag_ratio > 0.25 else 0)))

    # 6. hedging density
    hz = [h for h in HEDGES if re.search(r"\b" + re.escape(h) + r"\b", text, re.I)]
    hcount = sum(len(re.findall(r"\b" + re.escape(h) + r"\b", text, re.I)) for h in HEDGES)
    hdens = hcount * per1k
    sev = "WARN" if hdens > 8 else "OK"
    checks.append(("hedging", sev, hcount, (", ".join(hz[:6]) or "none") + f" ({hdens:.1f}/1k)",
                   (10 if hdens > 8 else 0)))

    # 7. vague attribution without specifics
    va = find_all(VAGUE_ATTRIB, text)
    sev = "WARN" if va else "OK"
    checks.append(("vague-attribution", sev, len(va), (", ".join(va[:4]) or "none"), len(va) * 8))

    # 8. em-dash clustering
    em = text.count("—") + text.count(" - ")
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    em_per_para = em / max(1, len(paras))
    sev = "WARN" if em_per_para > 1.5 else "OK"
    checks.append(("em-dash-clustering", sev, em, f"{em} em-dashes over {len(paras)} paragraphs", (8 if em_per_para > 1.5 else 0)))

    # 9. contractions present (their absence is a tell)
    contr = len(re.findall(r"\b\w+['’](t|s|re|ve|ll|d|m)\b", text, re.I))
    sev = "WARN" if contr == 0 and wc > 60 else "OK"
    checks.append(("contractions", sev, contr, ("none — formal/robotic" if contr == 0 else f"{contr} present"),
                   (10 if (contr == 0 and wc > 60) else 0)))

    # 10. list-heaviness (prose chopped into bullets)
    lines = [l for l in text.splitlines() if l.strip()]
    bullets = sum(1 for l in lines if re.match(r"\s*([-*•]|\d+\.)\s", l))
    ratio = bullets / max(1, len(lines))
    sev = "WARN" if ratio > 0.5 and len(lines) > 6 else "OK"
    checks.append(("list-heaviness", sev, bullets, f"{bullets}/{len(lines)} lines are bullets", (8 if (ratio > 0.5 and len(lines) > 6) else 0)))

    # 11. promotional gush (social/marketing slop the word-list misses: emoji,
    #     hashtag stacks, "thrilled to announce" openers, exclamation spray).
    promo_open = find_all([r"\b(thrilled|excited|humbled|honou?red|proud|delighted|pumped)\s+to\s+(announce|share|reveal)",
                           r"\bwithout further ado\b", r"\bhere'?s to\b", r"\bnext chapter\b"], text)
    emoji = re.findall(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF❤⭐✨]", text)
    hashtags = re.findall(r"(?:^|\s)#\w+", text)
    exclam = text.count("!")
    excl_dense = exclam * per1k > 6
    gush = len(promo_open) * 15 + min(12, len(emoji) * 4) + (10 if len(hashtags) >= 3 else 0) + (6 if excl_dense else 0)
    sev = "FAIL" if gush >= 15 else ("WARN" if gush > 0 else "OK")
    gdetail = []
    if promo_open: gdetail.append(f"opener '{promo_open[0]}'")
    if emoji: gdetail.append(f"{len(emoji)} emoji")
    if len(hashtags) >= 3: gdetail.append(f"{len(hashtags)} hashtags")
    if excl_dense: gdetail.append(f"{exclam} '!'")
    checks.append(("promotional-gush", sev, gush, (", ".join(gdetail) or "none"), min(30, gush)))

    # 12. low concreteness (generic abstraction with no anchors a real writer
    #     would have: numbers, names, or first-person). The essay-mill tell.
    digits = len(re.findall(r"\b\d[\d.,]*\b", text))
    firstp = len(re.findall(r"\b(I|I'?m|I'?ve|I'?ll|I'?d|my|me|we|our|us)\b", text))
    # proper nouns: capitalised word that is NOT the first token of its sentence
    propn = 0
    for s in sents:
        toks = re.findall(r"\b[A-Za-z][\w'-]*\b", s)
        for i, tk in enumerate(toks):
            if i > 0 and re.match(r"[A-Z][a-z]+", tk):
                propn += 1
    anchors = digits + firstp + propn
    density100 = anchors * 100.0 / wc
    lowconc = wc > 150 and density100 < 1.5
    sev = "FAIL" if lowconc else ("WARN" if (wc > 150 and density100 < 2.5) else "OK")
    checks.append(("low-concreteness", sev, round(density100, 2),
                   f"{anchors} anchors (nums+names+first-person) = {density100:.1f}/100 words; want >=2.5",
                   (18 if lowconc else (6 if (wc > 150 and density100 < 2.5) else 0))))

    score = min(100, sum(c[4] for c in checks))
    return {"word_count": wc, "sentences": len(sents), "checks": checks, "score": score}

def maybe_perplexity(text):
    try:
        import torch  # noqa
        from transformers import GPT2LMHeadModel, GPT2TokenizerFast
    except Exception:
        return None
    tok = GPT2TokenizerFast.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2"); model.eval()
    def ppl(t):
        import torch
        ids = tok(t, return_tensors="pt").input_ids
        if ids.shape[1] < 2: return float("nan")
        with torch.no_grad():
            out = model(ids[:, :1024], labels=ids[:, :1024])
        return math.exp(out.loss.item())
    sents = sentences(text)
    sp = [ppl(s) for s in sents if len(words(s)) >= 3]
    sp = [x for x in sp if not math.isnan(x)]
    return {"mean_perplexity": round(ppl(text), 1),
            "sentence_ppl_burstiness": round(stdev(sp), 1),
            "note": "higher perplexity & burstiness = more human (GPT-2 proxy)"}

PASS_BAR = 20  # score at or below this = passes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--text")
    ap.add_argument("--perplexity", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.text is not None:
        text = a.text
    elif a.path:
        text = open(a.path, encoding="utf-8").read()
    else:
        text = sys.stdin.read()

    r = analyze(text)
    if a.perplexity:
        p = maybe_perplexity(text)
        if p: r["perplexity"] = p

    has_fail = any(s == "FAIL" for (_, s, _, _, _) in r["checks"])
    passed = (r["score"] <= PASS_BAR) and not has_fail
    r["passed"] = passed

    if a.json:
        r["checks"] = [{"name": n, "severity": s, "count": c, "detail": d, "points": pt}
                       for (n, s, c, d, pt) in r["checks"]]
        print(json.dumps(r, indent=2));
        sys.exit(0 if passed else 1)

    print(f"\n  natural-writing slop report  —  {r['word_count']} words, {r['sentences']} sentences")
    print("  " + "-" * 66)
    icon = {"OK": "✓", "WARN": "!", "FAIL": "✗"}
    for (n, s, c, d, pt) in r["checks"]:
        print(f"  [{icon[s]}] {n:24s} {s:5s}  {d}")
    print("  " + "-" * 66)
    verdict = "PASS" if passed else "NEEDS WORK"
    reason = "" if passed else ("  (has a FAIL)" if has_fail else "  (score over bar)")
    print(f"  SLOP SCORE: {r['score']}/100   (bar: <= {PASS_BAR}, and no FAILs)   ->  {verdict}{reason}")
    if "perplexity" in r:
        pp = r["perplexity"]
        print(f"  GPT-2 perplexity: {pp['mean_perplexity']}   burstiness: {pp['sentence_ppl_burstiness']}   (higher = more human)")
    print()
    print("  Fix the FAIL/WARN lines above, then re-run. Aim for no FAILs and score <= 20.")
    print("  Note: a PASS means no crude tells were found — not a guarantee of 'human'.")
    print("  The binding check is the adversarial read described in SKILL.md.\n")
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
