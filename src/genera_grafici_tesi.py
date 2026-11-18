from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Individua la radice del progetto risalendo dalla posizione di questo script (src/ -> radice)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_figure_1_errori():
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

    # Ottimizza il layout aumentando lo spazio orizzontale tra i due sotto-grafici
    plt.tight_layout(w_pad=3.5)
    plt.subplots_adjust(wspace=0.35)

    output_file = DATA_DIR / 'confronto_errori_fp_fn.pdf'
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"✅ Figure_1 (Confronto Errori FP/FN) salvata in:\n   • {output_file}")


def generate_figure_2_corrected():
    rc_settings = {
        'font.size': 11,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'figure.autolayout': True
    }

    with plt.rc_context(rc_settings):
        # Dati ufficiali dell'Ablation Study (Media Globale)
        fpr = [9.61, 14.80, 10.45, 11.96]
        recall = [41.11, 41.21, 39.14, 46.05]

        # Etichette reali delle configurazioni
        labels = [
            'v5 (1,1,0)',
            'v5 (1,1,1) [AsymFlow]',
            'v6 (1,1,0)',
            'v6 (1,1,1) [WebProxy]'
        ]

        colors = ['#8c564b', '#e377c2', '#7f7f7f', '#17becf']
        markers = ['o', 's', 'o', '*']

        fig, ax = plt.subplots(figsize=(8, 5.5))

        for i in range(len(labels)):
            size = 220 if markers[i] == '*' else 110
            ax.scatter(fpr[i], recall[i], color=colors[i], marker=markers[i],
                       s=size, label=labels[i], edgecolor='black', zorder=3)

            # Posizionamento del testo vicino ai punti per evitare sovrapposizioni
            offsets = [(8, -12), (8, -12), (8, -12), (-110, 8)]
            ax.annotate(labels[i], (fpr[i], recall[i]), textcoords="offset points",
                        xytext=offsets[i], ha='left', fontsize=9.5,
                        fontweight='bold' if i == 3 else 'normal')

        # Freccia che indica la transizione da v5(1,1,1) a v6(1,1,1)
        ax.annotate('', xy=(11.96, 46.05), xytext=(14.80, 41.21),
                    arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7, alpha=0.5),
                    zorder=2)

        ax.set_xlabel('FPR Medio Globale (%) $\\rightarrow$ (Minore è meglio)', fontweight='bold')
        ax.set_ylabel('Recall Media Globale (%) $\\rightarrow$ (Maggiore è meglio)', fontweight='bold')
        ax.set_title('Analisi di Pareto: Trade-off FPR vs Recall (v5 vs v6)', fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6, zorder=0)

        ax.set_xlim(8.5, 16.0)
        ax.set_ylim(37.0, 48.0)

        pdf_path = DATA_DIR / "tradeoff_pareto_v5_v6.pdf"
        png_path = DATA_DIR / "tradeoff_pareto_v5_v6.png"

        plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
        plt.savefig(png_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Figure_2 (Analisi di Pareto) salvata in:\n   • {pdf_path}\n   • {png_path}")


if __name__ == "__main__":
    generate_figure_1_errori()
    generate_figure_2_corrected()
