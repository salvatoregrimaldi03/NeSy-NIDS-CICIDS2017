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
# 2. MAPPA FEATURE
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
    return {f: feature_names.index(f) for f in required_features}


# ============================================================
# 3. METRICHE DI VALUTAZIONE
# ============================================================

def evaluate_model(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        preds_probs = model(X_test).squeeze()
        preds_binary = (preds_probs >= 0.5).float().cpu().numpy()

    y_true = y_test.cpu().numpy()

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
# 4. TRAINING NEURO-SIMBOLICO MODULARE (ABLATION)
# ============================================================

def train_nesy_ltn_ablation(X_train, y_train, feature_names, input_dim, active_rules=(True, True, True), epochs=5,
                            batch_size=512):
    model = ClassifierNet(input_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    P = ltn.Predicate(model)
    Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
    Implies = ltn.Connective(ltn.fuzzy_ops.ImpliesReichenbach())
    Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier='f')
    SatAgg = ltn.fuzzy_ops.SatAgg(ltn.fuzzy_ops.AggregPMeanError(p=2))

    idx = get_feature_indices(feature_names)

    use_r1, use_r2, use_r3 = active_rules

    # Regola 1: High-Frequency Flood
    def high_frequency_flood_func(x):
        fwd_fps = x[:, idx['Fwd Packets/s']:idx['Fwd Packets/s'] + 1]
        iat_mean = x[:, idx['Flow IAT Mean']:idx['Flow IAT Mean'] + 1]
        score = (fwd_fps + (1.0 - iat_mean)) / 2.0
        return torch.clamp(score * 1.5, 0.0, 1.0)

    # Regola 2: Strict Micro-Flows
    def strict_micro_flows_func(x):
        std = x[:, idx['Packet Length Std']:idx['Packet Length Std'] + 1]
        avg_size = x[:, idx['Average Packet Size']:idx['Average Packet Size'] + 1]
        duration = x[:, idx['Flow Duration']:idx['Flow Duration'] + 1]
        avg_score = ((1.0 - std) + (1.0 - avg_size) + (1.0 - duration)) / 3.0
        score = torch.relu(avg_score - 0.85) * (1.0 / 0.15)
        return torch.clamp(score, 0.0, 1.0)

    # Regola 3: Asymmetric Flow Ratio
    def asymmetric_flow_ratio_func(x):
        fwd = x[:, idx['Total Fwd Packets']:idx['Total Fwd Packets'] + 1]
        bwd = x[:, idx['Total Backward Packets']:idx['Total Backward Packets'] + 1]
        ratio = fwd / (fwd + bwd + 1e-6)
        score = torch.relu(ratio - 0.75) * (1.0 / 0.25)
        return torch.clamp(score, 0.0, 1.0)

    HighFrequencyFlood = ltn.Predicate(func=high_frequency_flood_func)
    StrictMicroFlows = ltn.Predicate(func=strict_micro_flows_func)
    AsymmetricFlowRatio = ltn.Predicate(func=asymmetric_flow_ratio_func)

    dataset = TensorDataset(X_train, y_train)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
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
            if use_r1:
                rules.append(Forall(x_all, Implies(HighFrequencyFlood(x_all), P(x_all))))
            if use_r2:
                rules.append(Forall(x_all, Implies(StrictMicroFlows(x_all), P(x_all))))
            if use_r3:
                rules.append(Forall(x_all, Implies(AsymmetricFlowRatio(x_all), P(x_all))))

            sat_degree = SatAgg(*rules)
            loss = 1.0 - sat_degree
            loss.backward()
            optimizer.step()

    return model


# ============================================================
# 5. MAIN - ABLATION STUDY SU TUTTI GLI SCENARI
# ============================================================

if __name__ == "__main__":
    print("==================================================")
    print(" ABLATION STUDY: Analisi 2^3 Combinazioni Regole v5")
    print("==================================================")

    scenarios, feature_names = prepare_leave_one_out_scenarios()
    input_dim = len(feature_names)

    # Definizione delle 8 combinazioni
    combinations = [
        (False, False, False),  # Baseline (0,0,0)
        (True, False, False),  # Solo R1 (1,0,0)
        (False, True, False),  # Solo R2 (0,1,0)
        (False, False, True),  # Solo R3 (0,0,1)
        (True, True, False),  # R1 + R2 (1,1,0)
        (True, False, True),  # R1 + R3 (1,0,1)
        (False, True, True),  # R2 + R3 (0,1,1)
        (True, True, True)  # Completo v5 (1,1,1)
    ]

    combo_names = [
        "(0,0,0) Baseline LTN",
        "(1,0,0) Solo HighFrequencyFlood",
        "(0,1,0) Solo StrictMicroFlows",
        "(0,0,1) Solo AsymmetricFlowRatio",
        "(1,1,0) Flood + MicroFlows",
        "(1,0,1) Flood + AsymmetricRatio",
        "(0,1,1) MicroFlows + AsymmetricRatio",
        "(1,1,1) Modello Completo v5"
    ]

    ablation_results = {}

    for target_attack, sc in scenarios.items():
        print(f"\n==================================================")
        print(f" ESECUZIONE ABLATION STUDY: Attacco Target = [{target_attack}]")
        print(f"==================================================")

        X_train, y_train = sc['X_train'], sc['y_train']
        X_test_zd, y_test_zd = sc['X_test_zd'], sc['y_test_zd']

        scenario_res = {}

        for combo, name in zip(combinations, combo_names):
            print(f"  • Training combinazione: {name} ...", end="", flush=True)
            model = train_nesy_ltn_ablation(X_train, y_train, feature_names, input_dim, active_rules=combo, epochs=5)
            res = evaluate_model(model, X_test_zd, y_test_zd)

            scenario_res[name] = res
            print(
                f" -> Recall: {res['Recall']:.2f}% | Precision: {res['Precision']:.2f}% | F1: {res['F1']:.2f}% | FPR: {res['FPR']:.2f}%")

        ablation_results[target_attack] = scenario_res

    # Salvataggio JSON
    output_path = DATA_DIR / "ablation_study_results_v5.json"
    with open(output_path, "w") as f:
        json.dump(ablation_results, f, indent=4)

    print(f"\n==================================================")
    print(f"✅ ABLATION STUDY COMPLETATO CON SUCCESSO!")
    print(f"I risultati delle 8 combinazioni sono stati salvati in: {output_path}")
    print(f"==================================================")