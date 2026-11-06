from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Individua la radice del progetto risalendo dalla posizione di questo script (src/ -> radice)
BASE_DIR = Path(__file__).resolve().parent.parent

# Definisci la cartella di destinazione (usiamo 'data' / 'figure' per la tesi LaTeX)
output_dir = BASE_DIR / 'data'
output_dir.mkdir(parents=True, exist_ok=True)

# Dati estratti da error_analysis_comparativa2.json (Baseline 0,0,0 vs NeSy 1,1,1)
categories = ['DDoS', 'PortScan', 'Web Attacks', 'DoS']

# Conteggi FN
fn_baseline = [25395, 79335, 1075, 81178]
fn_nesy = [23360, 65393, 1078, 36442]

# Conteggi FP
fp_baseline = [686, 991, 770, 109]
fp_nesy = [9287, 9659, 2114, 33794]

x = np.arange(len(categories))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# Grafico Falsi Negativi (FN)
ax1.bar(x - width/2, fn_baseline, width, label='Baseline (0,0,0)', color='#a0a0a0')
ax1.bar(x + width/2, fn_nesy, width, label='NeSy LTN (1,1,1)', color='#1f77b4')
ax1.set_title('Falsi Negativi (FN) - Minacce Mancate')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.set_yscale('log')  # Scala logaritmica per gestire le differenti magnitudini
ax1.set_ylabel('Numero Campioni (Scala Log)')
ax1.legend()
ax1.grid(True, which="both", ls="--", alpha=0.3)

# Grafico Falsi Positivi (FP)
ax2.bar(x - width/2, fp_baseline, width, label='Baseline (0,0,0)', color='#a0a0a0')
ax2.bar(x + width/2, fp_nesy, width, label='NeSy LTN (1,1,1)', color='#d62728')
ax2.set_title('Falsi Positivi (FP) - Falsi Allarmi')
ax2.set_xticks(x)
ax2.set_xticklabels(categories)
ax2.set_yscale('log')
ax2.set_ylabel('Numero Campioni (Scala Log)')
ax2.legend()
ax2.grid(True, which="both", ls="--", alpha=0.3)

# Ottimizza il layout aumentando lo spazio orizzontale tra i due sotto-grafici (w_pad)
plt.tight_layout(w_pad=3.5)
plt.subplots_adjust(wspace=0.35)  # Garantisce un margine orizzontale generoso tra i due assi

# Salvataggio con percorso risolto
output_file = output_dir / 'confronto_errori_fp_fn.pdf'
plt.savefig(output_file, dpi=300)
print(f"Grafico generato e salvato con successo in: {output_file}")
plt.show()