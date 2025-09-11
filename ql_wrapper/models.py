from QuantLib import *
import math
import random
from random import gauss

class BlackScholesModel:
    def __init__(self, spot, strike_price, risk_free_rate, volatility):
        self.today = Date().todaysDate()
        Settings.instance().evaluationDate = self.today

        self.spot_handle = QuoteHandle(SimpleQuote(spot))

        day_count = Actual365Fixed()
        self.rate_curve = YieldTermStructureHandle(
            FlatForward(self.today, risk_free_rate, day_count)
        )

        self.vol_curve = BlackVolTermStructureHandle(
            BlackConstantVol(self.today, NullCalendar(), volatility, day_count)
        )

        self.bs_process = BlackScholesProcess(
            self.spot_handle,
            self.rate_curve,
            self.vol_curve
        )
    
    def price(self, option_obj):

        payoff = PlainVanillaPayoff(option_obj.type, option_obj.strike)
        exercise = EuropeanExercise(option_obj.maturity)
        ql_option = VanillaOption(payoff, exercise)
        engine = AnalyticEuropeanEngine(self.bs_process)
        ql_option.setPricingEngine(engine)

        return ql_option.NPV()
        
    def greeks(self, option_obj):
        payoff = PlainVanillaPayoff(option_obj.type, option_obj.strike)
        exercise = EuropeanExercise(option_obj.maturity)
        ql_option = VanillaOption(payoff, exercise)

        engine = AnalyticEuropeanEngine(self.bs_process)
        ql_option.setPricingEngine(engine)

        return{
            'delta': ql_option.delta(),
            'gamma': ql_option.gamma(),
            'vega': ql_option.vega(),
            'theta': ql_option.theta(),

            }


class MonteCarloModel:
    def __init__(self, spot, risk_free_rate, volatility, num_paths=10000):
        self.spot = spot
        self.r = risk_free_rate
        self.vol = volatility
        self.num_paths = num_paths
    

    def price(self, option_obj, num_paths=None):
        day_count = Actual365Fixed()
        T = day_count.yearFraction(Date().todaysDate(), option_obj.maturity)
        if T <= 0:
            return 0.0
        N = num_paths or self.num_paths
        payoffs = []
        for _ in range(N):
            Z = random.gauss(0, 1)
            ST = self.spot * math.exp((self.r - 0.5 * self.vol ** 2) * T + self.vol * math.sqrt(T) * Z)
            if option_obj.type == Option.Call:
                payoff = max(ST - option_obj.strike, 0.0)
            else:
                payoff = max(option_obj.strike - ST, 0.0)
            discounted = math.exp(-self.r * T) * payoff
            payoffs.append(discounted)
        return sum(payoffs) / N
    
    def price_and_se(self, option_obj, num_paths=None):
        '''return (price, standard_error) for a european option via one-step MC.'''
        N = num_paths or self.num_paths
        day_count = Actual365Fixed(); today = Date().todaysDate()
        T = day_count.yearFraction(today, option_obj.maturity)
        if T <= 0:
            return 0.0, 0.0
        r = float(self.r)
        vol = float(self.vol)
        S0 = float(self.spot); K = float(option_obj.strike)
        disc = math.exp(-r * T)
        mu = (r - 0.5 * vol * vol) * T
        sig = vol * math.sqrt(T)
        payoffs = []

        for _ in range(N):
            Z = gauss(0.0, 1.0)
            ST = S0 * math.exp(mu + sig * Z)
            if option_obj.type == Option.Call:
                payoff = max(ST - K, 0.0)
            else:
                payoff = max(K - ST, 0.0)
            payoffs.append(payoff)
        mean_payoff = sum(payoffs) / N
        var_payoff = (sum((x - mean_payoff)**2 for x in payoffs) / (N-1)) if N > 1 else 0.0
        price = disc * mean_payoff
        se = disc * math.sqrt(var_payoff / N)
        return price, se
    
    def delta(self, option_obj, bump=0.10, num_paths=None):
        '''Finite-difference Delta: (P(S0+bump) - P(S0-bump)) / (2*bump).'''
        S0_orig = float(self.spot)
        try:
            self.spot = S0_orig + bump
            up_price, _ = self.price_and_se(option_obj, num_paths=num_paths)
            self.spot = S0_orig - bump
            dn_price, _= self.price_and_se(option_obj, num_paths=num_paths)
        finally:
            self.spot = S0_orig
        return (up_price - dn_price ) / (2.0 * bump)
    
    def gamma(self, option_obj, bump=0.10, num_paths=None):
        '''Central-difference gamma: (P(S0+b) - 2*P(S0) + P(S0-b)) / b**2'''
        S0_orig = float(self.spot)
        S0_up = S0_orig + bump
        S0_dn = S0_orig - bump
        try:
            self.spot = S0_up
            up_price, _ = self.price_and_se(option_obj, num_paths=num_paths)
            self.spot = S0_orig
            mid_price, _ = self.price_and_se(option_obj, num_paths=num_paths)
            self.spot = S0_dn
            down_price, _ = self.price_and_se(option_obj, num_paths=num_paths)
        finally:
            self.spot = S0_orig

        return (up_price - 2.0 * mid_price + down_price) / (bump*bump)

        