import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg") # Evita il caricamento di librerie grafiche/Tkinter su Windows
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
input_path = DATA_DIR / "ablation_study_results_v6.json"

with open(input_path, 'r') as f:
    data = json.load(f)

attacchi = list(data.keys())  # ['DDoS', 'PortScan', 'Web Attacks', 'DoS']
configs = list(data[attacchi[0]].keys())

# ==============================================================================
# 1. CALCOLO MACRO-MEDIE 
# ==============================================================================
overall_metrics = {}
for cfg in configs:
    macro_recall = np.mean([data[atk][cfg]["Recall"] for atk in attacchi])
    macro_fpr = np.mean([data[atk][cfg]["FPR"] for atk in attacchi])
    overall_metrics[cfg] = {"Recall": macro_recall, "FPR": macro_fpr}

fpr_values = [overall_metrics[cfg]["FPR"] for cfg in configs]
recall_values = [overall_metrics[cfg]["Recall"] for cfg in configs]

# ==============================================================================
# 2. GRAFICO FIGURA 4.2: Trade-off FPR vs Recall Globale (Macro-Medie v6)
# ==============================================================================
plt.figure(figsize=(10.5, 6.2))
plt.scatter(fpr_values, recall_values, color='steelblue', s=100, alpha=0.85, edgecolors='black', zorder=3)

# Offset dedicati (dx, dy in punti) per evitare qualsiasi sovrapposizione nel cluster
label_offsets = {
    "(0,0,0) Baseline LTN": (10, -4),
    "(0,0,1) Solo WebToolProxy": (10, -13),
    "(1,0,0) Solo HighFrequencyFlood": (-42, 8),
    "(0,1,0) Solo StrictMicroFlows": (10, 6),
    "(1,0,1) Flood + WebToolProxy": (10, -2),
    "(0,1,1) MicroFlows + WebToolProxy": (10, -11),
    "(1,1,0) Flood + MicroFlows": (10, -3),
    "(1,1,1) Modello Completo v6": (-12, -16),
}

for i, cfg in enumerate(configs):
    short_label = cfg.split(')')[0] + ')'
    dx, dy = label_offsets.get(cfg, (8, 0))

    if cfg == "(1,1,1) Modello Completo v6":
        plt.scatter(fpr_values[i], recall_values[i], color='forestgreen', s=160, edgecolors='black', zorder=5)
        plt.annotate(
            f"Migliore {short_label}",
            (fpr_values[i], recall_values[i]),
            xytext=(dx, dy),
            textcoords='offset points',
            ha='right',
            fontsize=10,
            fontweight='bold',
            color='forestgreen'
        )
    elif cfg == "(0,0,0) Baseline LTN":
        plt.scatter(fpr_values[i], recall_values[i], color='firebrick', s=160, edgecolors='black', zorder=5)
        plt.annotate(
            f"Baseline {short_label}",
            (fpr_values[i], recall_values[i]),
            xytext=(dx, dy),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            color='firebrick'
        )
    else:
        plt.annotate(
            short_label,
            (fpr_values[i], recall_values[i]),
            xytext=(dx, dy),
            textcoords='offset points',
            fontsize=9.5
        )

plt.title('Ablation Study (v6): Trade-off tra FPR Medio e Recall Media Globale', fontsize=13.5)
plt.xlabel('False Positive Rate (FPR) Medio Complessivo [%]', fontsize=11.5)
plt.ylabel('Recall Media Complessiva [%]', fontsize=11.5)
plt.xlim(-0.3, 13.8)
plt.ylim(22.5, 49.5)
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(DATA_DIR / 'tradeoff_fpr_recall2.pdf', format='pdf', bbox_inches='tight')
plt.close()

# ==============================================================================
# 3. Confronto Baseline (0,0,0) vs NeSy (1,1,0) - Versione v6
# ==============================================================================
baseline_key = "(0,0,0) Baseline LTN"
nesy_110_key = "(1,1,0) Flood + MicroFlows"
nesy_111_key = "(1,1,1) Modello Completo v6"

baseline_recall = [data[atk][baseline_key]["Recall"] for atk in attacchi]
nesy_110_recall = [data[atk][nesy_110_key]["Recall"] for atk in attacchi]
nesy_111_recall = [data[atk][nesy_111_key]["Recall"] for atk in attacchi]

x = np.arange(len(attacchi))
width = 0.35

plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width / 2, baseline_recall, width, label='Baseline Neurale (0,0,0)', color='lightgray', edgecolor='black')
bars2 = plt.bar(x + width / 2, nesy_110_recall, width, label='Modello NeSy (1,1,0) - v6', color='steelblue', edgecolor='black')

plt.title('Confronto Recall per Categoria di Attacco: Baseline vs NeSy (1,1,0)', fontsize=13.5)
plt.ylabel('Recall [%]', fontsize=11.5)
plt.xticks(x, attacchi, fontsize=11)
plt.ylim(0, 105)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.6)

for bar in bars1 + bars2:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 1.5, f'{yval:.2f}%', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(DATA_DIR / 'confronto_attacchi_110_v6.pdf', format='pdf', bbox_inches='tight')
plt.close()

# ==============================================================================
# 4. Confronto Baseline (0,0,0) vs NeSy Completo (1,1,1) - v6
# ==============================================================================
plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width / 2, baseline_recall, width, label='Baseline Neurale (0,0,0)', color='lightgray', edgecolor='black')
bars2 = plt.bar(x + width / 2, nesy_111_recall, width, label='Modello NeSy Completo (1,1,1)', color='steelblue', edgecolor='black')

plt.title('Confronto Recall per Categoria di Attacco (Contesto Zero-Day)', fontsize=13.5)
plt.ylabel('Recall [%]', fontsize=11.5)
plt.xticks(x, attacchi, fontsize=11)
plt.ylim(0, 105)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.6)

for bar in bars1 + bars2:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 1.5, f'{yval:.2f}%', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(DATA_DIR / 'confronto_attacchi2.pdf', format='pdf', bbox_inches='tight')
plt.close()

print("Grafici v6 aggiornati generati con successo in:", DATA_DIR)
