# demos/export_jsons.py
import json
import os
from policybrain.normalize import normalize_policy

OUT = "out"
os.makedirs(OUT, exist_ok=True)

def write(name: str, obj):
    path = os.path.join(OUT, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj.to_json(), f, ensure_ascii=False, indent=2)
    print(f"✅ Wrote {path}")

def main():
    te_path = "data/Policy_Wordings/TravelEasy Policy QTD032212.pdf"
    sc_path = "data/Policy_Wordings/Scootsurance QSR022206_updated.pdf"

    te = normalize_policy(te_path, "TravelEasy")
    sc = normalize_policy(sc_path, "Scootsurance")

    write("TravelEasy", te)
    write("Scootsurance", sc)

if __name__ == "__main__":
    main()
