from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'figure.autolayout': True
})


def generate_figure_2_corrected():
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
    print(f"✅ Figure_2 aggiornata salvata in:\n   • {pdf_path}\n   • {png_path}")


if __name__ == "__main__":
    generate_figure_2_corrected()