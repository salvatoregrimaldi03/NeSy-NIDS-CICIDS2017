from pathlib import Path
import pandas as pd
import numpy as np

# Saliamo di un livello (da src a NeSy_PoC) per trovare la cartella data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
WEB_ATTACK_FILE = DATA_DIR / "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv"


def inspect_web_attack_features():
    if not WEB_ATTACK_FILE.exists():
        print(f"❌ File non trovato in: {WEB_ATTACK_FILE}")
        return

    print(f"📖 Lettura di: {WEB_ATTACK_FILE.name}...")
    df = pd.read_csv(WEB_ATTACK_FILE)
    df.columns = df.columns.str.strip()
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    df['Is_Attack'] = (df['Label'] != 'BENIGN').astype(int)

    print(f"\n📊 Distribuzione campioni:")
    print(df['Label'].value_counts())

    # Feature candidate come proxy L4/TCP
    candidate_features = [
        'PSH Flag Count',
        'ACK Flag Count',
        'Init_Win_bytes_forward',
        'Init_Win_bytes_backward',
        'Bwd Packet Length Mean',
        'Bwd Packet Length Std',
        'Average Packet Size',
        'Flow Duration',
        'Fwd Packets/s',
        'URG Flag Count'
    ]

    # Verifica quali feature sono effettivamente presenti nel CSV
    available_features = [f for f in candidate_features if f in df.columns]

    print("\n" + "=" * 70)
    print(f"{'FEATURE L4 PROXY':<30} | {'BENIGN (Medio)':<18} | {'ATTACK (Medio)':<18}")
    print("=" * 70)

    benign_mask = df['Is_Attack'] == 0
    attack_mask = df['Is_Attack'] == 1

    for feat in available_features:
        mean_benign = df.loc[benign_mask, feat].mean()
        mean_attack = df.loc[attack_mask, feat].mean()

        print(f"{feat:<30} | {mean_benign:<18.4f} | {mean_attack:<18.4f}")

    print("=" * 70)


if __name__ == "__main__":
    inspect_web_attack_features()