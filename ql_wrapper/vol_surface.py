from QuantLib import (Settings, Date, BlackVarianceSurface, QuoteHandle, SimpleQuote,
                      Actual365Fixed, NullCalendar, DateParser)
import csv
from typing import List, Tuple

def read_chain_csv(filepath: str) -> List[Tuple[Date, float, float]]:
    """Read an option chain CSV (expiry,strike,iv) and return [(Date, strike, iv)] tuples."""
    rows: List[Tuple[Date, float, float]] = []

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expiry = DateParser.parseISO(row["expiry"])
            strike = float(row["strike"])
            iv = float(row["iv"])
            rows.append((expiry, strike, iv))

        return rows

def build_vol_surface(chain_data: List[Tuple[Date, float, float]]) -> BlackVarianceSurface:
    Settings.instance().evaluationDate = Date.todaysDate()
    cal = NullCalendar()
    dc = Actual365Fixed()
    dates = sorted({d for (d, _, _) in chain_data})
    strikes = sorted({k for (_, k, _) in chain_data})
    iv_map = {(d, k): iv for (d, k, iv) in chain_data}
    today = Settings.instance().evaluationDate
    vol_matrix = [[iv_map[(d, k)] for k in strikes] for d in dates]
    surface = BlackVarianceSurface(today, cal, dates, strikes, vol_matrix, dc)
    return surface



