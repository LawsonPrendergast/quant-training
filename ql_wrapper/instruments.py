from QuantLib import *

class Instrument:
    def __init__(self, notional, maturity):
        self.notional = notional
        self.maturity = maturity

    def price(self, model):
        raise NotImplementedError

    def greeks(self, model):
        raise NotImplementedError

class EuropeanOption(Instrument):
    def __init__(self, strike, maturity, option_type):
        super().__init__(notional=1.0, maturity=maturity)
        self.strike = strike
        self.type = option_type

    def price(self, model):
        return model.price(self)

    def greeks(self, model):
        return model.greeks(self) 

    
      