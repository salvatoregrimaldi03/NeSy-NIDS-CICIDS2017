import json
import matplotlib.pyplot as plt
import numpy as np
from preprocess import DATA_DIR


# 1. CARICAMENTO DATI REALI
input_path = DATA_DIR / "ablation_study_results_v5.json"
with open(input_path, 'r') as f:
    data = json.load(f)

# Estraiamo la lista degli attacchi e delle configurazioni dal JSON
attacchi = list(data.keys())  # ['DDoS', 'PortScan', 'Web Attacks', 'DoS']
configs = list(data[attacchi[0]].keys())

# ==========================================
# CALCOLO METRICHE GLOBALI PER IL TRADE-OFF
# ==========================================
overall_metrics = {}
for cfg in configs:
    total_tp = 0
    total_fn = 0
    total_fp = 0
    total_tn = 0

    for atk in attacchi:
        total_tp += data[atk][cfg]["TP"]
        total_fn += data[atk][cfg]["FN"]
        total_fp += data[atk][cfg]["FP"]
        total_tn += data[atk][cfg]["TN"]

    # Calcolo in percentuale
    overall_recall = (total_tp / (total_tp + total_fn)) * 100
    overall_fpr = (total_fp / (total_fp + total_tn)) * 100
    overall_metrics[cfg] = {"Recall": overall_recall, "FPR": overall_fpr}

fpr_values = [overall_metrics[cfg]["FPR"] for cfg in configs]
recall_values = [overall_metrics[cfg]["Recall"] for cfg in configs]

# ==========================================
# GRAFICO 1: Trade-off FPR vs Recall (Scatter)
# ==========================================
plt.figure(figsize=(10, 6))
plt.scatter(fpr_values, recall_values, color='steelblue', s=100, alpha=0.8, edgecolors='black')

# Aggiungo etichette e coloro in modo diverso la Baseline e la (1,1,0)
for i, cfg in enumerate(configs):
    label = cfg.split(')')[0] + ')'  # Prende solo la parte "(X,Y,Z)" per abbreviare

    if cfg == "(1,1,0) Flood + MicroFlows":
        plt.scatter(fpr_values[i], recall_values[i], color='forestgreen', s=150, edgecolors='black', zorder=5)
        plt.annotate("Migliore " + label, (fpr_values[i] + 0.3, recall_values[i] - 0.2), fontsize=10, fontweight='bold',
                     color='forestgreen')
    elif cfg == "(0,0,0) Baseline LTN":
        plt.scatter(fpr_values[i], recall_values[i], color='firebrick', s=150, edgecolors='black', zorder=5)
        plt.annotate("Baseline " + label, (fpr_values[i] + 0.3, recall_values[i] - 0.2), fontsize=10, fontweight='bold',
                     color='firebrick')
    else:
        plt.annotate(label, (fpr_values[i] + 0.3, recall_values[i] - 0.2), fontsize=9)

plt.title('Ablation Study: Trade-off tra False Positive Rate e Recall Globale', fontsize=14)
plt.xlabel('False Positive Rate (FPR) Complessivo [%]', fontsize=12)
plt.ylabel('Recall Complessiva [%]', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Salvataggio in PDF come richiesto dalle linee guida
plt.tight_layout()
plt.savefig(DATA_DIR / 'tradeoff_fpr_recall.pdf', format='pdf', bbox_inches='tight')
plt.show()

# ==========================================
# GRAFICO 2: Confronto Baseline vs NeSy (1,1,0) per Attacco
# ==========================================
baseline_key = "(0,0,0) Baseline LTN"
nesy_key = "(1,1,0) Flood + MicroFlows"

# I valori nel JSON sono già in percentuale
baseline_recall = [data[atk][baseline_key]["Recall"] for atk in attacchi]
nesy_recall = [data[atk][nesy_key]["Recall"] for atk in attacchi]

x = np.arange(len(attacchi))
width = 0.35

plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width / 2, baseline_recall, width, label='Baseline Neurale (0,0,0)', color='lightgray',
                edgecolor='black')
bars2 = plt.bar(x + width / 2, nesy_recall, width, label='Modello NeSy (1,1,0)', color='steelblue', edgecolor='black')

plt.title('Confronto Recall per Categoria di Attacco (Contesto Zero-Day)', fontsize=14)
plt.ylabel('Recall [%]', fontsize=12)
plt.xticks(x, attacchi, fontsize=11)
plt.ylim(0, 105)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Aggiungo i valori percentuali sopra le barre
for bar in bars1 + bars2:
    yval = bar.get_height()
    # Se il valore è molto basso (es. Web Attacks) lo sposto leggermente più su per renderlo leggibile
    offset = 1.5 if yval < 5 else 1.5
    plt.text(bar.get_x() + bar.get_width() / 2, yval + offset, f'{yval:.2f}%', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(DATA_DIR / 'confronto_attacchi.pdf', format='pdf', bbox_inches='tight')
plt.show()