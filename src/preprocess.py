import os
from pathlib import Path
import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import gc

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Mappatura dei file sui gruppi di attacco principali
FILE_ATTACK_MAP = {
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv": "DDoS",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv": "PortScan",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv": "Web Attacks",
    "Wednesday-workingHours.pcap_ISCX.csv": "DoS"
}


def clean_and_prepare(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    # Riduzione impronta di memoria (downcasting a float32 e int32)
    for col in df.columns:
        if df[col].dtype == np.float64:
            df[col] = df[col].astype(np.float32)
        elif df[col].dtype == np.int64:
            df[col] = df[col].astype(np.int32)

    return df


def map_label(raw_label, default_attack_name):
    raw_label_str = str(raw_label).strip()
    if raw_label_str == 'BENIGN':
        return 'BENIGN'
    return default_attack_name


def load_all_datasets():
    print(f"Caricamento dati dalla cartella: {DATA_DIR}")
    dfs = []

    for filename, attack_group in FILE_ATTACK_MAP.items():
        file_path = DATA_DIR / filename
        if not file_path.exists():
            print(f"⚠️  Attenzione: File '{filename}' non trovato in {DATA_DIR}, ignorato.")
            continue
        print(f"  • Lettura di {filename} ({attack_group})...")
        df = clean_and_prepare(file_path)
        df['Attack_Group'] = df['Label'].apply(lambda x: map_label(x, attack_group))
        df['Is_Attack'] = (df['Attack_Group'] != 'BENIGN').astype(np.int8)
        dfs.append(df)

    if not dfs:
        raise FileNotFoundError("Nessun file CSV valido trovato nella cartella data/")

    # Intersezione delle feature comuni
    common_cols = set(dfs[0].columns)
    for df in dfs[1:]:
        common_cols = common_cols.intersection(set(df.columns))

    exclude_cols = {'Label', 'Attack_Group', 'Is_Attack'}
    feature_cols = sorted(list(common_cols - exclude_cols))

    print(f"\nFeature comuni identificate tra tutti i dataset: {len(feature_cols)}")

    full_df = pd.concat([df[feature_cols + ['Attack_Group', 'Is_Attack']] for df in dfs], ignore_index=True)

    # Pulizia memoria intermedia
    del dfs
    gc.collect()

    return full_df, feature_cols


def prepare_leave_one_out_scenarios():
    full_df, feature_cols = load_all_datasets()

    available_attacks = [g for g in full_df['Attack_Group'].unique() if g != 'BENIGN']
    print(f"\nGruppi di attacco disponibili per la rotazione: {available_attacks}")

    scenarios = {}

    for target_attack in available_attacks:
        print(f"\n--------------------------------------------------")
        print(f" Configurazione Scenario Zero-Day: Attacco Escluso = [{target_attack}]")
        print(f"--------------------------------------------------")

        benign_df = full_df[full_df['Attack_Group'] == 'BENIGN']
        other_attacks_df = full_df[(full_df['Attack_Group'] != 'BENIGN') & (full_df['Attack_Group'] != target_attack)]
        target_attack_df = full_df[full_df['Attack_Group'] == target_attack]

        # 1. Split Benigno: 70% Train, 15% Validation, 15% Test
        benign_train, benign_val_test = train_test_split(benign_df, test_size=0.30, random_state=42)
        benign_val, benign_test = train_test_split(benign_val_test, test_size=0.50, random_state=42)

        # 2. Split Attacco Target Zero-Day
        target_val_df, target_test_df = train_test_split(target_attack_df, test_size=0.50, random_state=42)

        # 3. Assemblaggio Set
        train_df = pd.concat([benign_train, other_attacks_df], ignore_index=True)
        val_zd_df = pd.concat([benign_val, target_val_df], ignore_index=True)
        test_zd_df = pd.concat([benign_test, target_test_df], ignore_index=True)

        # Estrazione numpy arrays a precisione float32
        X_train_raw = train_df[feature_cols].values.astype(np.float32)
        y_train_raw = train_df['Is_Attack'].values.astype(np.float32)

        X_val_zd_raw = val_zd_df[feature_cols].values.astype(np.float32)
        y_val_zd_raw = val_zd_df['Is_Attack'].values.astype(np.float32)

        X_test_zd_raw = test_zd_df[feature_cols].values.astype(np.float32)
        y_test_zd_raw = test_zd_df['Is_Attack'].values.astype(np.float32)

        # Normalizzazione MinMaxScaler adattata rigorosamente SOLO sul Training Set
        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train_raw)
        X_val_zd_scaled = scaler.transform(X_val_zd_raw)
        X_test_zd_scaled = scaler.transform(X_test_zd_raw)

        scenarios[target_attack] = {
            'X_train': torch.tensor(X_train_scaled, dtype=torch.float32),
            'y_train': torch.tensor(y_train_raw, dtype=torch.float32),

            'X_val_zd': torch.tensor(X_val_zd_scaled, dtype=torch.float32),
            'y_val_zd': torch.tensor(y_val_zd_raw, dtype=torch.float32),

            'X_test_zd': torch.tensor(X_test_zd_scaled, dtype=torch.float32),
            'y_test_zd': torch.tensor(y_test_zd_raw, dtype=torch.float32),

            'X_train_unscaled': X_train_raw,
            'X_val_zd_unscaled': X_val_zd_raw,
            'X_test_zd_unscaled': X_test_zd_raw,

            'feature_names': feature_cols,
            'target_attack': target_attack,
            'scaler': scaler
        }

        print(f"  • Training Set: {len(train_df)} campioni (Benigni: {len(benign_train)}, Altri Attacchi: {len(other_attacks_df)})")
        print(f"  • Validation Set: {len(val_zd_df)} campioni (Benigni: {len(benign_val)}, Attacco '{target_attack}': {len(target_val_df)})")
        print(f"  • UNTOUCHED Test Set: {len(test_zd_df)} campioni (Benigni: {len(benign_test)}, Attacco '{target_attack}': {len(target_test_df)})")

        # Pulizia della memoria al termine di ogni scenario
        del train_df, val_zd_df, test_zd_df
        gc.collect()

    del full_df
    gc.collect()

    return scenarios, feature_cols


if __name__ == "__main__":
    scenarios, features = prepare_leave_one_out_scenarios()
    print("\nPreprocessing completato con successo per tutti gli scenari!")
