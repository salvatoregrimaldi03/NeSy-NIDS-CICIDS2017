# NeSy-NIDS-CICIDS2017

## 📌 Che cos'è?
**NeSy-NIDS-CICIDS2017** è una repository Proof of Concept (PoC) che implementa un **Sistema Neuro-Simbolico per la Rilevazione delle Intrusioni di Rete (NeSy-NIDS)** valutato sul dataset benchmark **CICIDS2017**. Il framework combina architetture di reti neurali con il ragionamento simbolico per migliorare l'accuratezza nella rilevazione delle intrusioni, l'interpretabilità e la robustezza contro vettori di attacco zero-day.

Attualmente, la repository include:
- Script di preprocessing per l'estrazione delle feature e l'ispezione del traffico (`src/preprocess.py`, `src/inspect_web_attacks.py`).
- Pipeline principali di esecuzione e valutazione (`src/main.py`, `src/main_2.py`).
- Pipeline per studi di ablazione (`src/ablation_study.py`, `src/ablation_study_2.py`).
- Script per l'analisi comparativa degli errori (`src/error_analysis.py`, `src/error_analysis_2.py`).
- Benchmarking per la valutazione su rotazione zero-day (configurazioni `v1`-`v4`, `v6`, `v5123`).
- Strumenti di visualizzazione dei risultati (`src/genera_grafici.py`, `src/genera_grafici_tesi.py`).
- Gestione dello storage dei dataset ottimizzata tramite **Git LFS** per i file `.csv` di grandi dimensioni.

Le funzionalità principali includono:
- Organizzazione del progetto separata tra moduli Python in `src/` e stoccaggio di dataset CSV e log dei risultati in `data/`.
- Log completi dei risultati degli studi di ablazione (versioni `v5`, `v6`).
- Analisi comparativa degli errori per la validazione delle regole neuro-simboliche.
- Tracciamento trasparente dei dataset CSV di grandi dimensioni gestito via Git LFS.

## 🚀 Come provarlo
Il progetto può essere eseguito localmente in un ambiente Python.

### Configurazione ed Esecuzione
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
5. Esegui la pipeline principale di rilevazione delle intrusioni:
   ```bash
   python src/main.py
   ```

## 🧱 Sviluppato con
- [Python](https://www.python.org/) - Linguaggio di programmazione principale.
- [PyTorch](https://pytorch.org/) - Framework per l'addestramento e l'esecuzione delle reti neurali.
- [LTNtorch](https://github.com/logictensornetworks/LTNtorch) - Implementazione PyTorch di Logic Tensor Networks (LTN) per l'integrazione del ragionamento simbolico.
- [Scikit-Learn](https://scikit-learn.org/) - Per il preprocessing dei dati, la gestione delle feature e il calcolo delle metriche di valutazione.
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) - Per l'ispezione, la manipolazione e l'analisi vettoriale dei dati di traffico.
- [Matplotlib](https://matplotlib.org/) - Per la generazione dei grafici e la visualizzazione dei risultati sperimentali.
- [Git LFS](https://git-lfs.github.com/) - Per il tracciamento e la gestione dello storage dei file CSV di grandi dimensioni.

## 🔗 Risorse correlate
- [CICIDS2017 Dataset (Ufficiale)](https://www.unb.ca/cic/datasets/ids-2017.html) - Benchmark ufficiale pubblicato dal Canadian Institute for Cybersecurity (UNB).
- [CICIDS2017 Dataset (Kaggle)](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset) - Mirror Kaggle (curato da Chethan H N) da cui sono stati scaricati i file CSV impiegati nel progetto.
