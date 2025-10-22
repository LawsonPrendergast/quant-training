from typing import Optional, Union
from QuantLib import YieldTermStructureHandle, FlatForward, Actual365Fixed, BlackVolTermStructureHandle, BlackConstantVol, Settings, QuoteHandle, SimpleQuote, NullCalendar
import csv

class MarketParams:
    def __init__(self, spot: float, risk_free_rate: float, div_yield: float = 0.0, vol: Optional[float] = None):
        self.spot = float(spot)
        self._spot_quote = SimpleQuote(self.spot)
        self.r = float(risk_free_rate)
        self.q = float(div_yield)
        self.vol = None if vol is None else float(vol)
        self._vol_surface_handle = None

    @property
    def spot_handle(self) -> QuoteHandle:
        return QuoteHandle(self._spot_quote)

    @property
    def r_handle(self) -> YieldTermStructureHandle:
        today = Settings.instance().evaluationDate
        return YieldTermStructureHandle(FlatForward(today, self.r, Actual365Fixed()))
    
    @property
    def q_handle(self) -> YieldTermStructureHandle:
        today = Settings.instance().evaluationDate
        return YieldTermStructureHandle(FlatForward(today, self.q, Actual365Fixed()))
    
    @property
    def vol_handle(self) -> Optional[BlackVolTermStructureHandle]:
        if self._vol_surface_handle is not None:
            return self._vol_surface_handle
        
        if self.vol is None:
            return None
        today = Settings.instance().evaluationDate
        return BlackVolTermStructureHandle(BlackConstantVol(today, NullCalendar(), self.vol, Actual365Fixed()))
       

    def set_spot(self, new_spot: float):
        self._spot_quote.setValue(float(new_spot))
        self.spot = float(new_spot)
    
    def set_rate(self, new_r: float):
        self.r = float(new_r)
    
    def set_vol(self, new_vol: float):
        self.vol = float(new_vol)
    
    def set_vol_surface(self, surface: BlackVolTermStructureHandle):
        '''Set a vol surface to use'''
        self._vol_surface_handle = surface
    
    def load_from_csv(self, filepath: str) -> None:
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            lower = {k.strip().lower(): v for k, v in row.items()}
            self.set_spot(float(lower.get("spot", self.spot)))
            self.set_rate(float(lower.get("risk_free_rate", self.r)))
            if "div_yield" in lower and lower['div_yield'] not in ("", None):
                self.q = float(lower['div_yield'])
            if "vol" in lower and lower['vol'] not in ("", None):
                self.set_vol(float(lower['vol']))


    