# NeSy-NIDS-CICIDS2017
<div>
   <a href="#italiano"><img src="https://img.shields.io/badge/ITALIANO-009246?style=for-the-badge&logoColor=white" height="35" alt="Italiano"></a>
   <a href="#english"><img src="https://img.shields.io/badge/ENGLISH-012169?style=for-the-badge&logoColor=white" height="35" alt="English"></a>
   <br><br>
</div>

<a id="italiano"></a>
## Italiano

### 📌 Che cos'è?
**NeSy-NIDS-CICIDS2017** è una repository Proof of Concept (PoC) che implementa un **Sistema Neuro-Simbolico per la Rilevazione delle Intrusioni di Rete (NeSy-NIDS)** valutato sul dataset benchmark **CICIDS2017**. Il framework combina architetture di reti neurali con il ragionamento simbolico (*Logic Tensor Networks*) per migliorare l'accuratezza nella rilevazione delle intrusioni, l'interpretabilità e la robustezza contro vettori di attacco zero-day.

#### Metodologia di Validazione (Leave-One-Out Zero-Day)
Per simulare scenari di attacco inediti, la valutazione adotta un protocollo **Leave-One-Out** sulle 4 famiglie di attacco principali del dataset (`DDoS`, `PortScan`, `Web Attacks`, `DoS`): in ogni esperimento il modello viene addestrato sul traffico benigno e su 3 famiglie di attacco note, per poi essere testato sulla 4ª famiglia completamente esclusa dalla fase di training.

Attualmente, la repository include:
- Script di preprocessing per la pulizia dei dati, la creazione degli split *leave-one-out* e l'ispezione del traffico (`src/preprocess.py`, `src/inspect_web_attacks.py`).
- Pipeline principali di esecuzione e valutazione per i set di regole `v5` e `v6` (`src/main.py`, `src/main_2.py`).
- Pipeline per studi di ablazione (`src/ablation_study.py`, `src/ablation_study_2.py`).
- Script per l'analisi comparativa degli errori FP/FN (`src/error_analysis.py`, `src/error_analysis_2.py`).
- Benchmarking per la valutazione su rotazione zero-day (configurazioni `v1`-`v4`, `v6`, `v5123`).
- Strumenti di visualizzazione dei risultati e generazione delle figure (`src/genera_grafici.py`, `src/genera_grafici_2.py`, `src/genera_grafici_tesi.py`).
- Gestione dello storage dei dataset ottimizzata tramite **Git LFS** per i file `.csv` di grandi dimensioni.

## Risultati Principali (Confronto v5 vs v6)

La tabella riporta le **macro-medie globali** calcolate sui quattro scenari *zero-day* del protocollo *Leave-One-Attack-Out* (LOAO) sotto ciclo di valutazione unificato. La tripla `(R1, R2, R3)` indica i vincoli logici attivi durante l'addestramento:
- **R1 (`HighFrequencyFlood`):** rileva traffico ad elevata frequenza di pacchetti.
- **R2 (`StrictMicroFlows`):** identifica flussi brevi con pochi pacchetti.
- **R3:** euristica di sessione (`AsymmetricFlowRatio` nella **v5**, sostituita da `WebToolProxy` nella **v6**).

| Configurazione | Recall medio (%) ↑ | F1-Score medio (%) ↑ | FPR medio (%) ↓ |
| :--- | :---: | :---: | :---: |
| `v5 (1,1,0)` | 41,11 | 46,97 | 9,61 |
| `v5 (1,1,1)` — *AsymmetricFlowRatio* | 41,21 | 45,08 | 14,80 |
| `v6 (1,1,0)` | 39,14 | 44,24 | 10,45 |
| **`v6 (1,1,1)` — *WebToolProxy*** | **46,04** | **50,74** | **11,96** |

### Grafici Vettoriali (PDF)
- [Studio di ablazione v6: trade-off FPR/Recall ed effetto di R3](data/tradeoff_fpr_recall2.pdf)
- [Recall zero-day per categoria: Baseline vs NeSy v6 (1,1,0)](data/confronto_attacchi_110_v6.pdf)
- [Recall zero-day per categoria: Baseline vs NeSy v6 Completo (1,1,1)](data/confronto_attacchi2.pdf)
- [Analisi degli errori: conteggi Falsi Positivi (FP) e Falsi Negativi (FN)](data/confronto_errori_fp_fn.pdf)

### 🚀 Come provarlo
Il progetto può essere eseguito localmente in un ambiente Python.

> **Prerequisiti:** [Python 3.10+](https://www.python.org/) (testato su `3.10.12`) e [Git LFS](https://git-lfs.com/) installati sul sistema. Prima di scaricare i file CSV del dataset, assicurati di aver inizializzato Git LFS almeno una volta:
> ```bash
> git lfs install
> ```

#### Configurazione ed Esecuzione
1. Clona la repository:
   ```bash
   git clone https://github.com/salvatoregrimaldi03/NeSy-NIDS-CICIDS2017.git
   ```
2. Entra nella cartella del progetto:
   ```bash
   cd NeSy-NIDS-CICIDS2017
   ```
3. Scarica i file CSV del dataset tramite Git LFS:
   ```bash
   git lfs pull
   ```
4. Crea e attiva un ambiente virtuale Python:
   ```bash
   python -m venv .venv
   # Su Windows:
   .venv\Scripts\activate
   # Su Linux/macOS:
   source .venv/bin/activate
   ```
5. Installa le dipendenze necessarie:
   ```bash
   pip install torch scikit-learn pandas numpy matplotlib
   pip install https://github.com/logictensornetworks/LTNtorch/archive/refs/heads/main.zip
   ```
6. Esegui la pipeline principale di rilevazione delle intrusioni:
   ```bash
   # Esecuzione con set di regole v5:
   python src/main.py
   # Oppure con set di regole v6:
   python src/main_2.py
   ```

### 🧱 Sviluppato con
- [Python](https://www.python.org/) - Linguaggio di programmazione principale.
- [PyTorch](https://pytorch.org/) - Framework per l'addestramento e l'esecuzione delle reti neurali.
- [LTNtorch](https://github.com/logictensornetworks/LTNtorch) - Implementazione PyTorch di Logic Tensor Networks (LTN) per l'integrazione del ragionamento simbolico.
- [Scikit-Learn](https://scikit-learn.org/) - Per il preprocessing dei dati, la gestione delle feature e il calcolo delle metriche di valutazione.
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) - Per l'ispezione, la manipolazione e l'analisi vettoriale dei dati di traffico.
- [Matplotlib](https://matplotlib.org/) - Per la generazione dei grafici e la visualizzazione dei risultati sperimentali.
- [Git LFS](https://git-lfs.github.com/) - Per il tracciamento e la gestione dello storage dei file CSV di grandi dimensioni.

### 🔗 Risorse correlate
- [CICIDS2017 Dataset (Ufficiale)](https://www.unb.ca/cic/datasets/ids-2017.html) - Benchmark ufficiale pubblicato dal Canadian Institute for Cybersecurity (UNB).
- [CICIDS2017 Dataset (Kaggle)](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset) - Mirror Kaggle (curato da Chethan H N) da cui sono stati scaricati i file CSV impiegati nel progetto.

 <a id="english"></a>
## English

### 📌 What is it?

**NeSy-NIDS-CICIDS2017** is a Proof of Concept (PoC) repository that implements a **Neuro-Symbolic Network Intrusion Detection System (NeSy-NIDS)** evaluated on the **CICIDS2017** benchmark dataset. The framework combines neural network architectures with symbolic reasoning (Logic Tensor Networks) to improve intrusion detection accuracy, interpretability, and robustness against zero-day attack vectors.

#### Validation Methodology (Leave-One-Out Zero-Day)
To simulate unseen attack scenarios, the evaluation follows a Leave-One-Out protocol across the 4 main attack families in the dataset (`DDoS`, `PortScan`, `Web Attacks`, `DoS`): in each run, the model is trained on benign traffic and 3 known attack families, and then evaluated on the 4th attack family completely held out during training.

The repository currently includes:

- Preprocessing scripts for data cleaning, leave-one-out split creation, and traffic inspection (`src/preprocess.py`, `src/inspect_web_attacks.py`).
- Main execution and evaluation pipelines for rule sets `v5` and `v6` (`src/main.py`, `src/main_2.py`).
- Pipelines for ablation studies (`src/ablation_study.py`, `src/ablation_study_2.py`).
- Scripts for comparative FP/FN error analysis (`src/error_analysis.py`, `src/error_analysis_2.py`).
- Benchmarking tools for evaluation under zero-day rotation (configurations `v1`–`v4`, `v6`, `v5123`).
- Tools for visualizing experimental results and generating thesis figures (`src/genera_grafici.py`, `src/genera_grafici_2.py`, `src/genera_grafici_tesi.py`).
- Optimized dataset storage management through **Git LFS** for large `.csv` files.

## Main Results (v5 vs v6 Comparison)

The table below reports the **global macro-averages** computed across the four *zero-day* scenarios of the *Leave-One-Attack-Out* (LOAO) protocol under a unified evaluation cycle. The `(R1, R2, R3)` tuple indicates which logical constraints are active during training:
- **R1 (`HighFrequencyFlood`):** detects traffic with a high packet transmission rate.
- **R2 (`StrictMicroFlows`):** identifies short flows with a low packet count.
- **R3:** session heuristic (`AsymmetricFlowRatio` in **v5**, replaced by `WebToolProxy` in **v6**).

| Configuration | Mean Recall (%) ↑ | Mean F1-Score (%) ↑ | Mean FPR (%) ↓ |
| :--- | :---: | :---: | :---: |
| `v5 (1,1,0)` | 41.11 | 46.97 | 9.61 |
| `v5 (1,1,1)` — *AsymmetricFlowRatio* | 41.21 | 45.08 | 14.80 |
| `v6 (1,1,0)` | 39.14 | 44.24 | 10.45 |
| **`v6 (1,1,1)` — *WebToolProxy*** | **46.04** | **50.74** | **11.96** |

### Vector Plots (PDF)
- [v6 Ablation Study: FPR/Recall trade-off and impact of R3](data/tradeoff_fpr_recall2.pdf)
- [Zero-day Recall by attack category: Baseline vs NeSy v6 (1,1,0)](data/confronto_attacchi_110_v6.pdf)
- [Zero-day Recall by attack category: Baseline vs Full NeSy v6 (1,1,1)](data/confronto_attacchi2.pdf)
- [Error Analysis: False Positive (FP) and False Negative (FN) counts](data/confronto_errori_fp_fn.pdf)

### 🚀 How to try it

The project can be run locally in a Python environment.

> **Prerequisites:** [Python 3.10+](https://www.python.org/) (tested on `3.10.12`) and [Git LFS](https://git-lfs.com/) installed on your system. Before downloading the dataset CSV files, make sure Git LFS is initialized:
> ```bash
> git lfs install
> ```

#### Setup and Execution

1. Clone the repository:
   ```bash
   git clone https://github.com/salvatoregrimaldi03/NeSy-NIDS-CICIDS2017.git
   ```

2. Navigate to the project directory:
   ```bash
   cd NeSy-NIDS-CICIDS2017
   ```

3. Download the dataset CSV files using Git LFS:
   ```bash
   git lfs pull
   ```

4. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

5. Install the required dependencies:
   ```bash
   pip install torch scikit-learn pandas numpy matplotlib
   pip install https://github.com/logictensornetworks/LTNtorch/archive/refs/heads/main.zip
   ```

6. Run the main intrusion detection pipeline:
   ```bash
   # Run with v5 rule set:
   python src/main.py
   # Or run with v6 rule set:
   python src/main_2.py
   ```

### 🧱 Built with

- [Python](https://www.python.org/) - Main programming language.
- [PyTorch](https://pytorch.org/) - Framework for training and running neural networks.
- [LTNtorch](https://github.com/logictensornetworks/LTNtorch) - PyTorch implementation of Logic Tensor Networks (LTN) for integrating symbolic reasoning.
- [Scikit-Learn](https://scikit-learn.org/) - Used for data preprocessing, feature management, and evaluation metric computation.
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) - Used for inspecting, manipulating, and performing vectorized analysis of network traffic data.
- [Matplotlib](https://matplotlib.org/) - Used to generate plots and visualize experimental results.
- [Git LFS](https://git-lfs.github.com/) - Used for tracking and managing the storage of large CSV files.

### 🔗 Related Resources

- [CICIDS2017 Dataset (Official)](https://www.unb.ca/cic/datasets/ids-2017.html) - Official benchmark dataset published by the Canadian Institute for Cybersecurity (UNB).
- [CICIDS2017 Dataset (Kaggle)](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset) - Kaggle mirror (curated by Chethan H N) from which the CSV files used in this project were downloaded.
