from QuantLib import Date, Option as QLOption
from typing import Optional, Any, Dict


class Instrument:
    def __init__(self, notional, maturity: Date, model: Optional[Any] = None, **kwargs: Any) -> None:
        self.notional = float(notional); self.maturity = maturity; self.model = model
        self.meta: Dict[str, Any] = dict(kwargs)

    def set_model(self, model: Any) -> None:
        self.model = model
    

    def price(self, model: Optional[Any] = None, **kwargs: Any) -> float:
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No pricing model provided: pass model=... or call set_model(..)")
        return mdl.price(self, **kwargs)

    def greeks(self, model: Optional[Any] = None, **kwargs: Any):
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No pricing model provided: pass model=... or call set_model(...)")
        if hasattr(mdl, "greeks"):
            return mdl.greeks(self, **kwargs)
        raise AttributeError("Model does not implement greeks().")

'''class EuropeanOption(Instrument):
    def __init__(self, strike, maturity, option_type, pricing_model=None, **kwargs):
        super().__init__(notional=1.0, maturity=maturity, model=pricing_model, **kwargs)
        self.strike = float(strike)
        self.option_type = option_type

    def price(self, model, **kwargs):
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No pricing model provided.")
        return mdl.price(self, **kwargs)

    def greeks(self, model=None, **kwargs):
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No pricing model provided.")
        return mdl.greeks(self, **kwargs) '''

    
class Option(Instrument):
    def __init__(self, strike, maturity_date, option_type, style="European", underlying="Equity", pricing_model=None, **kwargs):
        super().__init__(notional=1.0, maturity=maturity_date, model=pricing_model, **kwargs)
        self.strike = float(strike)
        self.option_type = option_type
        self.underlying = underlying
        self.style = style
        if self.style not in {"European", "American"}:
            raise ValueError(f"Unsupported option style: {self.style}")
        if self.underlying not in {"Equity", "FX"}:
            raise ValueError(f"Unsupported underlying type: {self.underlying}")
        

    def delta(self, model=None, **kwargs):
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No pricing model provided.")
        if hasattr(mdl, "delta"):
            return mdl.delta(self,**kwargs)
        if hasattr(mdl, "greeks"):
            g = mdl.greeks(self, **kwargs)
            if isinstance(g, dict) and "delta" in g:
                return g["delta"]
        raise AttributeError("Model does not implement delta() or greeks().")
    
    def gamma(self, model=None, **kwargs):
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No Pricing model provided.")
        if hasattr(mdl, "gamma"):
            return mdl.gamma(self, **kwargs)
        if hasattr(mdl, "greeks"):
            g = mdl.greeks(self, **kwargs)
            if isinstance(g, dict) and "gamma" in g:
                return g["gamma"]
        raise AttributeError("Model does not implement gamma() or greeks()")

    def vega(self, model=None, **kwargs):
        mdl = model or self.model
        if mdl is None:
            raise ValueError("No pricing model provided")
        if hasattr(mdl, "vega"):
            return mdl.vega(self, **kwargs)
        if hasattr(mdl, "greeks"):
            g = mdl.greeks(self, **kwargs)
            if isinstance(g, dict) and "vega" in g:
                return g["vega"]
        raise AttributeError("Model does not implement vega() or greeks()")
