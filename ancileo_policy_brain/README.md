# ancileo_policy_brain

Policy & Document Intelligence (Blocks 1 + 3) starter kit.

## Quickstart

```bash
cd ancileo_policy_brain
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Add PDFs into data/Policy_Wordings/
# - TravelEasy Policy QTD032212.pdf
# - Scootsurance QSR022206_updated.pdf
# (Optionally add a flight booking PDF to data/samples/flight_sg_to_tyo.pdf)
python demos/demo_compare_medical.py
python demos/demo_trip_extract.py
python demos/demo_quote.py
```
