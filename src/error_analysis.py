import json
import torch
import numpy as np
from preprocess import prepare_leave_one_out_scenarios, DATA_DIR
from ablation_study import train_nesy_ltn_ablation


def run_comparative_error_analysis():
    print("==================================================")
    print(" ERROR ANALYSIS COMPARATIVA: Baseline (0,0,0) vs NeSy (1,1,0)")
    print("==================================================")

    # 1. Caricamento dati
    scenarios, feature_names = prepare_leave_one_out_scenarios()
    input_dim = len(feature_names)

    # 2. Feature focus per regole 1 e 2
    key_features = [
        'Fwd Packets/s', 'Flow IAT Mean',
        'Packet Length Std', 'Average Packet Size', 'Flow Duration'
    ]
    key_indices = [feature_names.index(f) for f in key_features]

    def get_mean_stats(X_subset):
        if len(X_subset) == 0:
            return {feat: 0.0 for feat in key_features}
        return {feat: float(np.mean(X_subset[:, idx])) for feat, idx in zip(key_features, key_indices)}

    analysis_results = {}

    for target_attack, sc in scenarios.items():
        print(f"\nAnalisi comparativa per lo scenario: [{target_attack}]")

        X_train, y_train = sc['X_train'], sc['y_train']
        X_test_zd, y_test_zd = sc['X_test_zd'], sc['y_test_zd']
        X_test_zd_unscaled = sc['X_test_zd_unscaled']
        y_true = y_test_zd.cpu().numpy()

        # --- A. BASELINE (0,0,0) ---
        print("  • Addestramento Baseline Neurale (0,0,0)...")
        model_base = train_nesy_ltn_ablation(
            X_train, y_train, feature_names, input_dim,
            active_rules=(False, False, False), epochs=5
        )
        model_base.eval()
        with torch.no_grad():
            preds_base = (model_base(X_test_zd).squeeze() >= 0.5).float().cpu().numpy()

        fp_base_mask = (y_true == 0) & (preds_base == 1)
        fn_base_mask = (y_true == 1) & (preds_base == 0)

        print(f"    -> Baseline ha prodotto: {np.sum(fp_base_mask)} FP | {np.sum(fn_base_mask)} FN")

        # --- B. NESY (1,1,0) ---
        print("  • Addestramento NeSy (1,1,0)...")
        model_nesy = train_nesy_ltn_ablation(
            X_train, y_train, feature_names, input_dim,
            active_rules=(True, True, False), epochs=5
        )
        model_nesy.eval()
        with torch.no_grad():
            preds_nesy = (model_nesy(X_test_zd).squeeze() >= 0.5).float().cpu().numpy()

        fp_nesy_mask = (y_true == 0) & (preds_nesy == 1)
        fn_nesy_mask = (y_true == 1) & (preds_nesy == 0)

        print(f"    -> NeSy (1,1,0) ha prodotto: {np.sum(fp_nesy_mask)} FP | {np.sum(fn_nesy_mask)} FN")

        # --- C. SALVATAGGIO STATISTICHE ---
        analysis_results[target_attack] = {
            "Baseline_000": {
                "FP_count": int(np.sum(fp_base_mask)),
                "FN_count": int(np.sum(fn_base_mask)),
                "FP_mean_features": get_mean_stats(X_test_zd_unscaled[fp_base_mask]),
                "FN_mean_features": get_mean_stats(X_test_zd_unscaled[fn_base_mask])
            },
            "NeSy_110": {
                "FP_count": int(np.sum(fp_nesy_mask)),
                "FN_count": int(np.sum(fn_nesy_mask)),
                "FP_mean_features": get_mean_stats(X_test_zd_unscaled[fp_nesy_mask]),
                "FN_mean_features": get_mean_stats(X_test_zd_unscaled[fn_nesy_mask])
            }
        }

    # 3. Salvataggio in JSON
    output_path = DATA_DIR / "error_analysis_comparativa.json"
    with open(output_path, "w") as f:
        json.dump(analysis_results, f, indent=4)

    print(f"\n✅ Analisi comparativa salvata in: {output_path}")


if __name__ == "__main__":
    run_comparative_error_analysis()