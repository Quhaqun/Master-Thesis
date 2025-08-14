# -*- coding: utf-8 -*-
"""
Erstellt Auswertungsplots aus allen CSVs in einem Ordner.
Alle PNGs werden im Unterordner "plots" gespeichert.
Im Plot "durchschnitt_pro_teilnehmer" werden nur Teilnehmernummern angezeigt.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------- Einstellungen ----------------------
folder_path = r"C:\Users\Quhaqu\Desktop\impotant csv"  # <--- anpassen
exclude_training = True

# Neuer Ordner für Plots
plot_dir = os.path.join(folder_path, "plots")
os.makedirs(plot_dir, exist_ok=True)

# Ausgabe-Dateien
OUT = {
    "paired": "paired_targets_selected.png",
    "per_trial": "targets_selected_per_trial.png",
    "delta": "delta_joint_minus_solo.png",
    "box": "boxplot_selected_by_condition.png",
    "acc_part": "accuracy_per_participant.png",
    "acc_trial": "accuracy_per_trial.png",
    "dbl_part": "doublesel_per_participant.png",
    "dbl_trial": "doublesel_per_trial.png",
    "rt_part": "reactiontimes_per_participant.png",
    "scatter": "scatter_selected_vs_accuracy.png",
    "table_ptp": "durchschnitt_pro_teilnehmer.csv",
}

def savefig_local(fig, name, folder=plot_dir, dpi=150):
    p = os.path.join(folder, name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight")
    print(f"Gespeichert: {p}")

# ---------------------- Laden & Aufbereiten ----------------------
def load_all_csvs(folder):
    dfs = []
    for f in glob.glob(os.path.join(folder, "*.csv")):
        try:
            df = pd.read_csv(f)
            if "Subnum" not in df.columns:
                df["Subnum"] = os.path.splitext(os.path.basename(f))[0]

            sel_cols = [c for c in df.columns if c.startswith("selobj") and "other" not in c]
            if not sel_cols:
                print(f"Warnung: {os.path.basename(f)} enthält keine selobj*-Spalten – übersprungen.")
                continue
            df["selected_count"] = df[sel_cols].notna().sum(axis=1)

            if "CONDITION" not in df.columns:
                print(f"Warnung: {os.path.basename(f)} ohne 'CONDITION' – übersprungen.")
                continue
            df["COND_GROUP"] = df["CONDITION"].astype(str).map(
                lambda s: "Solo" if "Solo" in s else ("Joint" if "Joint" in s else None)
            )
            if exclude_training:
                df = df[~df["CONDITION"].astype(str).str.contains("Training", na=False)]
            df = df[df["COND_GROUP"].isin(["Solo", "Joint"])]

            if {"player1correct","player1incorrect"}.issubset(df.columns):
                denom = (df["player1correct"].fillna(0) + df["player1incorrect"].fillna(0))
                df["player1_acc"] = np.where(denom>0, df["player1correct"].fillna(0)/denom, np.nan)
            else:
                df["player1_acc"] = np.nan

            if "doublesel" in df.columns:
                df["doublesel"] = pd.to_numeric(df["doublesel"], errors="coerce")
            else:
                df["doublesel"] = np.nan

            for rtcol in ["ReactiontimeSelection","ReactiontimeMarkall"]:
                if rtcol not in df.columns:
                    df[rtcol] = np.nan

            keep = ["Subnum","Trial","COND_GROUP","selected_count","player1_acc","doublesel",
                    "ReactiontimeSelection","ReactiontimeMarkall"]
            dfs.append(df[keep])
        except Exception as e:
            print(f"Fehler beim Lesen {f}: {e}")
    if not dfs:
        raise SystemExit("Keine geeigneten CSVs gefunden.")
    return pd.concat(dfs, ignore_index=True)

data = load_all_csvs(folder_path)

# ---------------------- Helper ----------------------
def mean_ci95(a):
    a = np.asarray(a, dtype=float)
    a = a[~np.isnan(a)]
    n = a.size
    if n <= 1: return np.nan, np.nan
    m = a.mean()
    se = a.std(ddof=1)/np.sqrt(n)
    return m, 1.96*se

# =================== A) Paired-Plot pro Teilnehmer ===================
ptp_sel = (data.groupby(["Subnum","COND_GROUP"])["selected_count"]
                .mean().reset_index().pivot(index="Subnum", columns="COND_GROUP", values="selected_count"))

ptp_sel_plot = ptp_sel.dropna(subset=["Solo","Joint"], how="any")

# Teilnehmernummern anstelle Namen im Index
ptp_sel_plot.index = range(1, len(ptp_sel_plot) + 1)

m_solo, ci_solo   = mean_ci95(ptp_sel_plot["Solo"].values)
m_joint, ci_joint = mean_ci95(ptp_sel_plot["Joint"].values)

fig, ax = plt.subplots(figsize=(7,6))
for _, r in ptp_sel_plot.iterrows():
    ax.plot([0,1],[r["Solo"], r["Joint"]], marker="o", alpha=0.25)
ax.errorbar([0,1],[m_solo,m_joint], yerr=[ci_solo,ci_joint],
            fmt="o", lw=0, elinewidth=2, capsize=5, color="black")
ax.set_xticks([0,1]); ax.set_xticklabels(["Solo","Joint"])
ax.set_ylabel("# Targets Selected")
ax.set_title("Targets Selected: Solo vs. Joint (Teilnehmer, verbunden)")
ax.grid(True, axis="y", alpha=0.3)
savefig_local(fig, OUT["paired"])
plt.close(fig)

# Tabelle rauslassen
ptp_sel.to_csv(os.path.join(plot_dir, OUT["table_ptp"]))
print(f"Gespeichert: {os.path.join(plot_dir, OUT['table_ptp'])}")

# =================== B) Ø pro Trial über TN ==========================
fig, ax = plt.subplots(figsize=(8,6))
for cond, g in data.groupby("COND_GROUP"):
    m = g.groupby("Trial")["selected_count"].mean()
    ax.plot(m.index, m.values, marker="o", label=cond)
ax.set_xlabel("Trial"); ax.set_ylabel("Ø # Targets Selected")
ax.set_title("Targets Selected pro Trial (Ø über alle Teilnehmer)")
ax.legend(title="Condition"); ax.grid(True, alpha=0.3)
savefig_local(fig, OUT["per_trial"])
plt.close(fig)

# =================== C) Delta (Joint - Solo) je Teilnehmer ===========
delta = (ptp_sel_plot["Joint"] - ptp_sel_plot["Solo"]).sort_values()
fig, ax = plt.subplots(figsize=(8,6))
ax.bar(range(len(delta)), delta.values)
ax.axhline(0, color="k", linewidth=1)
ax.set_xticks([])  # keine Namen
ax.set_ylabel("Δ Ø Auswahl (Joint − Solo)")
ax.set_title("Delta pro Teilnehmer")
savefig_local(fig, OUT["delta"])
plt.close(fig)

# =================== D) Boxplot Ø-Auswahl (Solo vs Joint) ============
fig, ax = plt.subplots(figsize=(6,6))
ax.boxplot(
    [ptp_sel_plot["Solo"].values, ptp_sel_plot["Joint"].values],
    tick_labels=["Solo", "Joint"], showfliers=False)
ax.set_ylabel("Ø # Targets Selected (Teilnehmer)")
ax.set_title("Verteilung Ø-Auswahl (Solo vs. Joint)")
savefig_local(fig, OUT["box"])
plt.close(fig)
