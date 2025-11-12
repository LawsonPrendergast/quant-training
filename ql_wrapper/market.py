from typing import Optional, Union
from QuantLib import RelinkableYieldTermStructureHandle, YieldTermStructureHandle, FlatForward, Actual365Fixed, RelinkableBlackVolTermStructureHandle, BlackVolTermStructureHandle, BlackConstantVol, Settings, QuoteHandle, SimpleQuote, NullCalendar
import csv

class MarketParams:
    def __init__(self, spot: float, risk_free_rate: float, div_yield: float = 0.0, vol: float | None = None, vol_handle=None):
        self.spot = float(spot)
        self._spot_quote = SimpleQuote(self.spot)
        self.r = float(risk_free_rate)
        self.q = float(div_yield)
        self.vol = None if vol is None else float(vol)
        
        self.day_count = Actual365Fixed()
        self.today = Settings.instance().evaluationDate

        self._spot_handle = QuoteHandle(self._spot_quote)

        # relinkable handles
        self._r_handle = RelinkableYieldTermStructureHandle()
        self._q_handle = RelinkableYieldTermStructureHandle()
        self._vol_handle = RelinkableBlackVolTermStructureHandle()

        # initial curves/surfaces + link
        self._r_curve = FlatForward(self.today, self.r, self.day_count)
        self._q_curve = FlatForward(self.today, self.q, self.day_count)
        if vol_handle is not None:
            # user-supplied surface/handle
            self._vol_surface = None
            if isinstance(vol_handle, BlackVolTermStructureHandle):
                # unwrap Handle -> underlying shared_ptr<BlackVolTermStructure>
                self._vol_handle.linkTo(vol_handle.currentLink())
            else:
                # assume a concrete BlackVolTermStructure object was provided
                self._vol_handle.linkTo(vol_handle)
        else:
            self._vol_surface = BlackConstantVol(
                self.today,
                NullCalendar(),
                self.vol if self.vol is not None else 0.0,
                self.day_count,
            )
            self._vol_handle.linkTo(self._vol_surface)

        self._r_handle.linkTo(self._r_curve)
        self._q_handle.linkTo(self._q_curve)


    @property
    def spot_handle(self) -> QuoteHandle:
        return self._spot_handle

    @property
    def r_handle(self) -> YieldTermStructureHandle:
        return self._r_handle
    
    @property
    def q_handle(self) -> YieldTermStructureHandle:
        return self._q_handle
    
    @property
    def vol_handle(self):
        return self._vol_handle
       

    def set_spot(self, new_spot: float):
        new_spot = float(new_spot)
        self._spot_quote.setValue(float(new_spot))
        self.spot = float(new_spot)
    
    def set_rate(self, new_r: float):
        self.r = float(new_r)
        self._r_curve = FlatForward(self.today, self.r, self.day_count)
        self._r_handle.linkTo(self._r_curve)
    
    def set_div(self, new_q: float):
        self.q = float(new_q)
        self._q_curve = FlatForward(self.today, self.q, self.day_count)
        self._q_handle.linkTo(self._q_curve)
    
    def set_vol(self, new_vol: float):
        self.vol = float(new_vol)
        self._vol_surface = BlackConstantVol(self.today, NullCalendar(), self.vol, self.day_count)
        self._vol_handle.linkTo(self._vol_surface)
    
    def set_vol_surface(self, surface):
        # accepts a surface OR a handle
        # If given a handle, link directly; if given a surface, wrap it
        if isinstance(surface, BlackVolTermStructureHandle):
            self._vol_surface = None
            self._vol_handle.linkTo(surface.currentLink())
        else:
            self._vol_surface = surface
            self._vol_handle.linkTo(self._vol_surface)

    
    def load_from_csv(self, filepath: str) -> None:
        with open(filepath, newline="") as f:
            row = next(csv.DictReader(f))
            lower = {k.strip().lower(): v for k, v in row.items()}
            if "spot" in lower and lower["spot"]:
                self.set_spot(float(lower["spot"]))
            if "risk_free_rate" in lower and lower["risk_free_rate"]:
                self.set_rate(float(lower["risk_free_rate"]))

            if "div_yield" in lower and lower['div_yield']:
                self.set_div(float(lower['div_yield']))
            if "vol" in lower and lower['vol']:
                self.set_vol(float(lower['vol']))


  