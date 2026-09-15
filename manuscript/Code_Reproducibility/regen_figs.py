#!/usr/bin/env python3
"""
Regenerate PLOS ONE figures to specification.

Fixes applied vs. the previous versions:
  * TrueType (fonttype 42) instead of Type 3 fonts
  * Arial (or Arial-metric-compatible Liberation Sans) instead of DejaVu
  * Explicit log-axis locators so tick labels no longer collide
  * Forest plots rebuilt from the shipped S8 XLSX, with the N >= 3 and
    CI-lower > 1 criteria enforced by assertion (the previous revision read a
    .docx that is not in the package, so Fig3(c) retained two N = 2 pairs)
  * Relative paths -- no hard-coded absolute paths
  * ROR = 1 reference line kept visible in every panel
  * All output within PLOS limits: 2.63-7.5 in wide, <= 8.75 in tall
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd
import os, textwrap

# ---------------------------------------------------------------- font setup
matplotlib.rcParams["ps.fonttype"] = 42      # TrueType, NOT Type 3
matplotlib.rcParams["pdf.fonttype"] = 42
avail = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
family = "Arial" if "Arial" in avail else ("Liberation Sans" if "Liberation Sans" in avail else "DejaVu Sans")
if family != "Arial":
    print(f"[font] WARNING: Arial not found; using {family}. The embedded EPS font "
          "name will not be ArialMT. Re-run where Arial is installed before upload.")
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = [family, "Arial", "Helvetica"]
print(f"[font] using: {family}")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "Figures")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- load S8
S8 = os.path.join(ROOT, "Supporting_Documents", "S8_Table_Complete_Signal_Detection_FULL.xlsx")
_s8 = pd.read_excel(S8)
rows = [dict(drug=r["Drug"], pt=r["Preferred Term"], n=int(r["N"]),
             ror=float(r["ROR"]), lo=float(r["ROR_CI_low"]),
             hi=float(r["ROR_CI_high"]), sig=str(r["ROR_signal"]).upper())
        for _, r in _s8.iterrows()]
signals = [r for r in rows if r["sig"] == "YES"]
# Hard guarantee: nothing below the pre-specified frequency threshold, and
# nothing whose CI crosses the null, can reach a figure.
assert min(r["n"] for r in signals) >= 3, "S8 flags a pair with N < 3 as a signal"
assert min(r["lo"] for r in signals) >= 1.0, "S8 flags a pair with CI lower bound < 1"
print(f"[data] S8 rows={len(rows)}  confirmed signals (N>=3, CI low>1)={len(signals)}")


def top_for(drug, k=12):
    """Top-k confirmed signals for a drug, ranked by case count."""
    sub = [r for r in signals if r["drug"].lower().startswith(drug.lower())]
    sub.sort(key=lambda r: (-r["n"], -r["ror"]))
    return sub[:k]


def forest(ax, data, title, colour):
    """Horizontal forest plot on a log ROR axis with non-colliding ticks."""
    if not data:
        ax.text(.5, .5, "No signals meeting criteria", ha="center",
                va="center", transform=ax.transAxes, fontsize=8)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.axis("off")
        return

    data = list(reversed(data))
    y = range(len(data))
    ror = [d["ror"] for d in data]
    lo = [max(d["lo"], 1e-3) for d in data]
    hi = [d["hi"] for d in data]

    ax.hlines(list(y), lo, hi, color=colour, lw=1.4, alpha=.75)
    ax.plot(ror, list(y), "o", color=colour, ms=5, zorder=3)
    ax.axvline(1, color="0.35", ls="--", lw=.9, zorder=1)

    ax.set_yticks(list(y))
    labs = ["\n".join(textwrap.wrap(f'{d["pt"]} (N={d["n"]})', 24)) for d in data]
    ax.set_yticklabels(labs, fontsize=7)
    ax.set_xscale("log")

    # explicit decade ticks -> no overlapping labels
    lo_e, hi_e = min(min(lo), 1.0), max(hi)   # keep ROR=1 line on-panel
    import math
    a, b = math.floor(math.log10(lo_e)), math.ceil(math.log10(hi_e))
    ticks = [10.0 ** e for e in range(a, b + 1)]
    if len(ticks) > 5:                      # thin out if too dense
        ticks = ticks[::2]
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(mticker.LogFormatterSciNotation())
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.tick_params(axis="x", labelsize=8)
    ax.set_xlim(lo_e * .5, hi_e * 2)

    ax.set_xlabel("ROR (95% CI)", fontsize=9)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.grid(axis="x", alpha=.25, lw=.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def save(fig, name, tight=False):
    for ext in ("eps", "png"):
        p = f"{OUT}/{name}.{ext}"
        fig.savefig(p, format=ext, dpi=300, facecolor="white", edgecolor="none",
                    **({"bbox_inches": "tight"} if tight else {}))
    plt.close(fig)
    w, h = fig.get_size_inches()
    print(f"[fig ] {name}: {w:.2f} x {h:.2f} in")


# ================================================== Fig 3
fig, axes = plt.subplots(1, 3, figsize=(7.5, 6.2))
for ax, (drug, label, col) in zip(axes, [
        ("Metformin",    "(a) Metformin",    "#C0392B"),
        ("Atorvastatin", "(b) Atorvastatin", "#2471A3"),
        ("Semaglutide",  "(c) Semaglutide",  "#1E8449")]):
    forest(ax, top_for(drug, 12), label, col)
fig.subplots_adjust(left=0.20, right=0.985, top=0.93, bottom=0.10, wspace=0.95)
save(fig, "Fig3")

# ================================================== Fig 4
fig, axes = plt.subplots(2, 2, figsize=(7.5, 7.4))
for ax, (drug, label, col) in zip(axes.ravel(), [
        ("Dapagliflozin",   "(a) Dapagliflozin",   "#8E44AD"),
        ("Insulin Glargine", "(b) Insulin glargine", "#D68910"),
        ("Tirzepatide",     "(c) Tirzepatide",     "#148F77"),
        ("Empagliflozin",   "(d) Empagliflozin",   "#B03A2E")]):
    forest(ax, top_for(drug, 8), label, col)
fig.subplots_adjust(left=0.19, right=0.985, top=0.945, bottom=0.085, wspace=0.95, hspace=0.42)
save(fig, "Fig4")


# ================================================== flowcharts
def box(ax, x, y, w, h, text, fc, fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=fc, edgecolor="#2C3E50", lw=1.1))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.45)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, color="#2C3E50", lw=1.1))


BLUE, GREEN, ORANGE, PURPLE, RED = "#D6EAF8", "#D5F5E3", "#FDEBD0", "#EBDEF0", "#FADBD8"

# ---- Fig 1
fig, ax = plt.subplots(figsize=(6.6, 8.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 15.2); ax.axis("off")
box(ax, 5, 14.3, 6.2, 1.15, "FAERS Database (2021Q1\u20132025Q4)\n7,612,804 raw report records", BLUE, bold=True)
arrow(ax, 5, 13.72, 5, 13.15)
box(ax, 5, 12.55, 6.2, 1.15, "After deduplication\n6,985,217 unique cases", BLUE)
ax.text(8.35, 12.55, "Excluded: 627,587\nduplicate case versions", fontsize=7, color="#B9770E",
        ha="center", va="center", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#B9770E", lw=.8))
arrow(ax, 5, 11.97, 5, 11.4)
box(ax, 5, 10.8, 6.2, 1.15, "Adolescents aged 12\u201317 years\n403,278 age-eligible reports", BLUE)
ax.text(8.35, 10.8, "Excluded: 6,581,939\nnon-adolescent reports", fontsize=7, color="#B9770E",
        ha="center", va="center", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#B9770E", lw=.8))
arrow(ax, 5, 10.22, 5, 9.65)
box(ax, 5, 9.05, 6.2, 1.05, "Drug panel filtering\n(anti-obesity + anti-diabetic medications)", GREEN)
arrow(ax, 5, 8.52, 5, 7.95)
for cx, txt in zip([1.55, 3.85, 6.15, 8.45], [
        "Broad obesity\n(14 drugs)\nN = 11,701", "Selected obesity\n(4 drugs)\nN = 10,701",
        "Broad diabetes\n(10 drugs)\nN = 5,208", "Selected diabetes\n(4 drugs)\nN = 342"]):
    box(ax, cx, 7.35, 2.15, 1.2, txt, ORANGE, fs=7.5)
    arrow(ax, cx, 6.72, 5, 6.15)
box(ax, 5, 5.5, 7.0, 1.35,
    "Disproportionality analysis\nROR, PRR, IC (BCPNN), EBGM (MGPS)\n"
    "Signal criteria: N \u2265 3, ROR 95% CI lower bound > 1;\nfour-metric concordance where all metrics available",
    PURPLE, fs=7.5)
arrow(ax, 5, 4.82, 5, 4.25)
box(ax, 5, 3.65, 7.0, 1.05, "Complementary ML analysis\nXGBoost case-level outcome triage; McNemar's test", RED, fs=7.5)
arrow(ax, 5, 3.12, 5, 2.55)
box(ax, 5, 1.85, 7.4, 1.35,
    "Results\nSOC-level AE distribution + PT-level signal forest plots\n"
    "+ drug-specific profiles + ML validation", BLUE, fs=7.5, bold=True)
save(fig, "Fig1", tight=True)

# ---- S1 Fig (detailed)
fig, ax = plt.subplots(figsize=(7.4, 8.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 16); ax.axis("off")
steps = [
    (15.1, "FAERS quarterly ASCII files, 2021Q1\u20132025Q4 (20 quarters)\nDEMO, DRUG, REAC, OUTC, THER, INDI, RPSR tables\n7,612,804 raw report records", BLUE, True),
    (13.3, "Deduplication\nMost recent case version retained per CASEID (FDA_DT)\n6,985,217 unique cases", BLUE, False),
    (11.5, "Age restriction\nPatients aged 12\u201317 years\n403,278 age-eligible reports", BLUE, False),
    (9.7,  "Drug-name normalisation\nRxNorm REST API \u2192 RxCUI;\nRapidFuzz secondary matching (threshold \u2265 85)", GREEN, False),
    (7.9,  "MedDRA coding\nEvents coded at Preferred Term (PT) level,\nmapped to SOC and HLGT", GREEN, False),
]
for y, txt, fc, bold in steps:
    box(ax, 5, y, 7.6, 1.45, txt, fc, fs=8, bold=bold)
for y in (15.1, 13.3, 11.5, 9.7):
    arrow(ax, 5, y - .78, 5, y - 1.05)
arrow(ax, 5, 7.9 - .78, 5, 6.85)
for cx, txt in zip([1.55, 3.85, 6.15, 8.45], [
        "Broad obesity\n14 drugs\nN = 11,701", "Selected obesity\n4 drugs\nN = 10,701",
        "Broad diabetes\n10 drugs\nN = 5,208", "Selected diabetes\n4 drugs\nN = 342"]):
    box(ax, cx, 6.2, 2.15, 1.25, txt, ORANGE, fs=7.5)
    arrow(ax, cx, 5.55, 5, 4.95)
box(ax, 5, 4.3, 7.6, 1.35,
    "Signal detection\n2,098 drug\u2013event pairs with N \u2265 2 evaluated;\n"
    "360 met criteria (N \u2265 3 and ROR 95% CI lower bound > 1)", PURPLE, fs=8)
arrow(ax, 5, 3.6, 5, 3.05)
box(ax, 5, 2.3, 7.6, 1.35,
    "Complementary ML triage\nTrain 2021Q1\u20132023Q4 | Validate 2024 | Test 2025\n"
    "XGBoost vs. baselines, McNemar's test", RED, fs=8)
save(fig, "S1_Fig_Detailed_Flowchart", tight=True)

print("\n[done] regenerated Fig1, Fig3, Fig4, S1_Fig")
print("[note] Fig2 (SOC distribution) and S2_Fig (SHAP) are NOT regenerated here:")
print("       Fig2 needs the licensed MedDRA PT->SOC mapping and S2_Fig needs the")
print("       trained model object; neither is redistributable in this package.")
