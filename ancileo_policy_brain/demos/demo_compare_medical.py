# demos/demo_compare_medical.py
from policybrain.normalize import normalize_policy
from policybrain.compare import compare_medical_md

def main():
    te = normalize_policy("data/Policy_Wordings/TravelEasy Policy QTD032212.pdf", "TravelEasy")
    sc = normalize_policy("data/Policy_Wordings/Scootsurance QSR022206_updated.pdf", "Scootsurance")
    print(compare_medical_md(te, sc))

if __name__ == "__main__":
    main()
