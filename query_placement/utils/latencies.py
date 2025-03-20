from csv import DictReader
from pathlib import Path


def fetch_latencies():
    """
    Fetch region latencies
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    latencies_csv = root_dir / "scripts" / "latencies.csv"
    latencies = {}
    
    with open(latencies_csv, encoding='utf-8', newline="") as csvfile:
        reader = DictReader(csvfile)
        # The first column is assumed to be the row region identifier.
        region_key = reader.fieldnames[0]
        for row in reader:
            region = row[region_key].strip()
            latencies[region] = {}
            for col in reader.fieldnames[1:]:
                latencies[region][col.strip()] = row[col].strip()
    return latencies