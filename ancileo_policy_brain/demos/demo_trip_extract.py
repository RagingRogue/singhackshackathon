# demos/demo_trip_extract.py
from policybrain.trip_extract import extract_trip_from_pdf

PDF = "data/samples/flight_sg_to_tyo.pdf"  # replace if needed

def main():
    trip = extract_trip_from_pdf(PDF)
    print(trip)

if __name__ == "__main__":
    main()
