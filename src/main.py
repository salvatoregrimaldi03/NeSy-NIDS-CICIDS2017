import json
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from preprocess import prepare_leave_one_out_scenarios, DATA_DIR
import ltn


# ============================================================
# 1. ARCHITETTURA DELLA RETE NEURALE
# ============================================================

class ClassifierNet(nn.Module):
    def __init__(self, input_dim):
        super(ClassifierNet, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.fc(x)


# ============================================================
# 2. INDICI DELLE FEATURE COMPORTAMENTALI (v5 Definitiva)
# ============================================================

def get_feature_indices(feature_names):
    required_features = [
        'Fwd Packets/s',
        'Flow IAT Mean',
        'Packet Length Std',
        'Average Packet Size',
        'Flow Duration',
        'Total Fwd Packets',
        'Total Backward Packets'
    ]

    missing_features = [f for f in required_features if (f not in feature_names)]
    if missing_features:
        raise ValueError(f"Feature mancanti nel dataset: {missing_features}")

    return {f: feature_names.index(f) for f in required_features}


# ============================================================
# 3. ADDESTRAMENTO RETE NEURALE CLASSICA (BCE)
# ============================================================

def train_classical_nn(X_train, y_train, input_dim, epochs=5, batch_size=512):
    print("\n  [1/2] Training Modello Neurale Classico (BCE Loss)...")
    model = ClassifierNet(input_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.BCELoss()

    dataset = TensorDataset(X_train, y_train.unsqueeze(1))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(loader)

    print(f"      Loss finale: {avg_loss:.4f}")
    return model


# ============================================================
# 4. ADDESTRAMENTO MODELLO NEURO-SIMBOLICO LTN (Regole v5)
# ============================================================

def train_nesy_ltn(X_train, y_train, feature_names, input_dim, epochs=5, batch_size=512):
    print("\n  [2/2] Training Modello Neuro-Simbolico (LTN Logic Rules v5)...")
    model = ClassifierNet(input_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Costrutti LTN
    P = ltn.Predicate(model)
    Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
    Implies = ltn.Connective(ltn.fuzzy_ops.ImpliesReichenbach())
    Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier='f')
    SatAgg = ltn.fuzzy_ops.SatAgg(ltn.fuzzy_ops.AggregPMeanError(p=2))

    idx = get_feature_indices(feature_names)

    # --- REGOLE V5: MACRO-COMPORTAMENTI CON SOGLIE E RAPPORTI RELATIVI ---

    # Regola 1: High-Frequency Flood (DDoS/DoS)
    def high_frequency_flood_func(x):
        fwd_fps = x[:, idx['Fwd Packets/s']:idx['Fwd Packets/s'] + 1]
        iat_mean = x[:, idx['Flow IAT Mean']:idx['Flow IAT Mean'] + 1]

        score = (fwd_fps + (1.0 - iat_mean)) / 2.0
        return torch.clamp(score * 1.5, 0.0, 1.0)

    # Regola 2: Strict Micro-Flows (PortScan)
    def strict_micro_flows_func(x):
        std = x[:, idx['Packet Length Std']:idx['Packet Length Std'] + 1]
        avg_size = x[:, idx['Average Packet Size']:idx['Average Packet Size'] + 1]
        duration = x[:, idx['Flow Duration']:idx['Flow Duration'] + 1]

        avg_score = ((1.0 - std) + (1.0 - avg_size) + (1.0 - duration)) / 3.0
        score = torch.relu(avg_score - 0.85) * (1.0 / 0.15)
        return torch.clamp(score, 0.0, 1.0)

    # Regola 3: Relative Asymmetry Ratio (Invariante alla scala)
    def asymmetric_flow_ratio_func(x):
        fwd = x[:, idx['Total Fwd Packets']:idx['Total Fwd Packets'] + 1]
        bwd = x[:, idx['Total Backward Packets']:idx['Total Backward Packets'] + 1]

        # Rapporto relativo di flusso con epsilon di stabilità numerica (1e-6)
        ratio = fwd / (fwd + bwd + 1e-6)

        # Si attiva se oltre il 75% dei pacchetti è inviato in una sola direzione
        score = torch.relu(ratio - 0.75) * (1.0 / 0.25)
        return torch.clamp(score, 0.0, 1.0)

    HighFrequencyFlood = ltn.Predicate(func=high_frequency_flood_func)
    StrictMicroFlows = ltn.Predicate(func=strict_micro_flows_func)
    AsymmetricFlowRatio = ltn.Predicate(func=asymmetric_flow_ratio_func)

    dataset = TensorDataset(X_train, y_train)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        total_sat = 0.0
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            mask_benign = (batch_y == 0)
            mask_attack = (batch_y == 1)

            rules = []
            if mask_benign.any():
                x_b = ltn.Variable("x_b", batch_x[mask_benign])
                rules.append(Forall(x_b, Not(P(x_b))))

            if mask_attack.any():
                x_a = ltn.Variable("x_a", batch_x[mask_attack])
                rules.append(Forall(x_a, P(x_a)))

            x_all = ltn.Variable("x_all", batch_x)
            rules.append(Forall(x_all, Implies(HighFrequencyFlood(x_all), P(x_all))))
            rules.append(Forall(x_all, Implies(StrictMicroFlows(x_all), P(x_all))))
            rules.append(Forall(x_all, Implies(AsymmetricFlowRatio(x_all), P(x_all))))

            sat_degree = SatAgg(*rules)
            loss = 1.0 - sat_degree
            loss.backward()
            optimizer.step()
            total_sat += sat_degree.item()

        avg_sat = total_sat / len(loader)

    print(f"      Satisfaction Degree finale: {avg_sat:.4f}")

    return model, {
        'high_frequency_flood_func': high_frequency_flood_func,
        'strict_micro_flows_func': strict_micro_flows_func,
        'asymmetric_flow_ratio_func': asymmetric_flow_ratio_func
    }


# ============================================================
# 5. ANALISI DETTAGLIATA REGOLE E FEATURE
# ============================================================

def analyze_rules_and_features(X_train_unscaled, X_test_zd_unscaled, X_test_zd_scaled, y_test_zd, feature_names,
                               rule_funcs):
    idx = get_feature_indices(feature_names)

    attack_mask = (y_test_zd == 1).cpu().numpy()
    X_zd_attack_scaled = X_test_zd_scaled[attack_mask]
    X_zd_attack_unscaled = X_test_zd_unscaled[attack_mask]

    act_flood = rule_funcs['high_frequency_flood_func'](X_zd_attack_scaled).cpu().numpy()
    act_micro = rule_funcs['strict_micro_flows_func'](X_zd_attack_scaled).cpu().numpy()
    act_asym = rule_funcs['asymmetric_flow_ratio_func'](X_zd_attack_scaled).cpu().numpy()

    rule_specs = [
        ('HighFrequencyFlood (v5)', idx['Fwd Packets/s'], act_flood),
        ('StrictMicroFlows (v5)', idx['Packet Length Std'], act_micro),
        ('AsymmetricFlowRatio (v5)', idx['Total Fwd Packets'], act_asym)
    ]

    analysis_res = {}
    for rule_name, f_idx, act_values in rule_specs:
        analysis_res[rule_name] = {
            'mean_rule_activation': float(np.mean(act_values)),
            'pct_samples_activated_gt_0.5': float(np.mean(act_values >= 0.5) * 100),
            'train_mean_unscaled_primary_feature': float(np.mean(X_train_unscaled[:, f_idx])),
            'zd_attack_mean_unscaled_primary_feature': float(np.mean(X_zd_attack_unscaled[:, f_idx]))
        }

    return analysis_res


# ============================================================
# 6. VALUTAZIONE MODELLI
# ============================================================

def evaluate_model(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        preds_probs = model(X_test).squeeze()
        preds_binary = (preds_probs >= 0.5).float().cpu().numpy()

    y_true = y_test.cpu().numpy()

    # Matrice di Confusione per FPR
    tn, fp, fn, tp = confusion_matrix(y_true, preds_binary, labels=[0, 1]).ravel()
    fpr = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0

    return {
        'Accuracy': float(accuracy_score(y_true, preds_binary) * 100),
        'Precision': float(precision_score(y_true, preds_binary, zero_division=0) * 100),
        'Recall': float(recall_score(y_true, preds_binary, zero_division=0) * 100),
        'F1': float(f1_score(y_true, preds_binary, zero_division=0) * 100),
        'FPR': float(fpr),
        'TN': int(tn),
        'FP': int(fp),
        'FN': int(fn),
        'TP': int(tp)
    }

# ============================================================
# 7. MAIN - ROTAZIONE AUTOMATICA ZERO-DAY REGOLE V5
# ============================================================

if __name__ == "__main__":
    print("==================================================")
    print(" ESPERIMENTO: Rotazione Zero-Day con Esclusione di un Singolo Attacco (Regole v5)")
    print("==================================================")

    scenarios, feature_names = prepare_leave_one_out_scenarios()
    input_dim = len(feature_names)

    all_results = {}

    for target_attack, sc in scenarios.items():
        print(f"\n==================================================")
        print(f" ESECUZIONE SCENARIO ZERO-DAY: Attacco Target = [{target_attack}]")
        print(f"==================================================")

        X_train, y_train = sc['X_train'], sc['y_train']

        # Usiamo il Test Set UNTOUCHED per le metriche ufficiali
        X_test_zd, y_test_zd = sc['X_test_zd'], sc['y_test_zd']

        # 1. Train Neurale Classica
        nn_model = train_classical_nn(X_train, y_train, input_dim, epochs=5)
        res_nn = evaluate_model(nn_model, X_test_zd, y_test_zd)

        # 2. Train NeSy (Rules v5)
        nesy_model, rule_funcs = train_nesy_ltn(X_train, y_train, feature_names, input_dim, epochs=5)
        res_nesy = evaluate_model(nesy_model, X_test_zd, y_test_zd)

        # 3. Analisi Regole v5 sul Test Set
        rule_analysis = analyze_rules_and_features(
            sc['X_train_unscaled'],
            sc['X_test_zd_unscaled'],
            X_test_zd,
            y_test_zd,
            feature_names,
            rule_funcs
        )

        # Stampa Risultati
        print(f"\n📊 --- Risultati Valutazione Zero-Day su [{target_attack}] ---")
        print(f"  • Rete Neurale Classica (BCE) -> Recall: {res_nn['Recall']:.2f}% | Precision: {res_nn['Precision']:.2f}% | F1: {res_nn['F1']:.2f}% | FPR: {res_nn['FPR']:.2f}%")
        print(f"  • Modello NeSy (LTN v5 Rules) -> Recall: {res_nesy['Recall']:.2f}% | Precision: {res_nesy['Precision']:.2f}% | F1: {res_nesy['F1']:.2f}% | FPR: {res_nesy['FPR']:.2f}%")
        print(f"\n🔍 --- Attivazione Regole v5 sull'attacco Zero-Day [{target_attack}] ---")
        for rule_name, metrics in rule_analysis.items():
            print(f"  • Regola [{rule_name}]:")
            print(f"      - Attivata nel {metrics['pct_samples_activated_gt_0.5']:.2f}% dei campioni (Grado medio: {metrics['mean_rule_activation']:.4f})")

        all_results[target_attack] = {
            'NN_Classical': res_nn,
            'NeSy_LTN_v5': res_nesy,
            'Rule_Analysis': rule_analysis
        }

    # Salvataggio Report JSON finale
    output_path = DATA_DIR / "zero_day_rotation_results_v5123.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=4)

    print(f"\n==================================================")
    print(f"✅ ESPERIMENTO COMPLETATO CON SUCCESSO!")
    print(f"I risultati dettagliati sono stati salvati in: {output_path}")
    print(f"==================================================")