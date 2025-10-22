from QuantLib import Settings, QuoteHandle, SimpleQuote, Actual365Fixed, YieldTermStructureHandle, FlatForward, BlackVolTermStructureHandle, BlackConstantVol, NullCalendar, BlackScholesProcess, PlainVanillaPayoff, EuropeanExercise, VanillaOption, AnalyticEuropeanEngine, BlackScholesMertonProcess
from QuantLib import Date, Option as QLOption
import math
import numpy as np

class BlackScholesModel:
    def __init__(self, spot=None, risk_free_rate=None, volatility=None, market=None):
        self.market = market
        self.today = Date().todaysDate()
        Settings.instance().evaluationDate = self.today

        self.spot_handle = (market.spot_handle if market is not None else QuoteHandle(SimpleQuote(float((spot)))))

        day_count = Actual365Fixed()
        
        if market is not None:
            self.rate_curve = market.r_handle
            self.vol_curve = (market.vol_handle if market.vol_handle is not None
                  else BlackVolTermStructureHandle(BlackConstantVol(self.today, NullCalendar(), float(volatility), day_count)))
        else:
            self.rate_curve = YieldTermStructureHandle(FlatForward(self.today, float(risk_free_rate), day_count))
            self.vol_curve = BlackVolTermStructureHandle(BlackConstantVol(self.today, NullCalendar(), float(volatility), day_count))

        # Dividend/foreign yield curve (q)
        self.div_curve = (market.q_handle if market is not None
                          else YieldTermStructureHandle(FlatForward(self.today, 0.0, day_count)))
        # Build generalized Black–Scholes process
        self.bs_process = BlackScholesMertonProcess(
            self.spot_handle,
            self.div_curve,
            self.rate_curve,
            self.vol_curve,
        )
    
    def price(self, instrument) -> float:
        process = BlackScholesMertonProcess(
            self.market.spot_handle,
            self.market.q_handle,
            self.market.r_handle,
            self.market.vol_handle)
        engine = AnalyticEuropeanEngine(process)
        payoff = PlainVanillaPayoff(instrument.option_type, instrument.strike)
        exercise = EuropeanExercise(instrument.maturity)
        ql_option = VanillaOption(payoff, exercise)
        ql_option.setPricingEngine(engine)

        return ql_option.NPV()
        
    def greeks(self, instrument):
        process = BlackScholesMertonProcess(self.market.spot_handle,
                                            self.market.q_handle,
                                            self.market.r_handle,
                                            self.market.vol_handle)
        engine = AnalyticEuropeanEngine(process)
        payoff = PlainVanillaPayoff(instrument.option_type, instrument.strike)
        exercise = EuropeanExercise(instrument.maturity)
        ql_option = VanillaOption(payoff, exercise)
        ql_option.setPricingEngine(engine)

        return{
            'delta': ql_option.delta(),
            'gamma': ql_option.gamma(),
            'vega': ql_option.vega(),
            'theta': ql_option.theta(),

            }


class MonteCarloModel:
    def __init__(self, spot, risk_free_rate, volatility, div_yield=0.0, num_paths=10000):
        self.spot = spot
        self.r = risk_free_rate
        self.q = div_yield
        self.vol = volatility
    

    def price(self, instrument, num_paths, seed=None, antithetic=False, control_variate=False):
        
        T = Actual365Fixed().yearFraction(Settings.instance().evaluationDate, instrument.maturity)
        if T <= 0:
            return 0.0
        N = num_paths
        r = float(self.r); q = float(self.q); vol = float(self.vol)
        S0 = float(self.spot)
        K = float(instrument.strike)
        disc = math.exp(-r * T)
        mu = (r - q - 0.5 * (vol**2)) * T
        sig = vol * math.sqrt(T)
        rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        if antithetic:
            half = N // 2
            Zs = rng.standard_normal(half)
            Zs = np.concatenate([Zs, -Zs])

        if not antithetic: Zs = rng.standard_normal(N)

        if Zs.size < N:  # if N is odd, add one extra draw
            Zs = np.concatenate([Zs, rng.standard_normal(1)])
    
        payoffs = []
        for Z in Zs:
            ST = S0 * math.exp(mu + sig * float(Z))
            if instrument.option_type == QLOption.Call:
                payoff = max(ST - K, 0.0)
            else:
                payoff = max(K - ST, 0.0)
            payoffs.append(payoff)
        price = disc * (sum(payoffs) / N)
        return price
    
    def price_and_se(self, instrument, num_paths, seed=None, antithetic=False, control_variate=False):
        '''return (price, standard_error) for a european option via one-step MC.'''
        T = Actual365Fixed().yearFraction(Settings.instance().evaluationDate, instrument.maturity)
        if T <= 0:
            return 0.0, 0.0
        N = num_paths
        S0 = float(self.spot)
        # Use NumPy RNG so seeding is effective; build Z draws (with optional antithetic pairing)
        rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        if antithetic:
            half = N // 2
            Zs = rng.standard_normal(half)
            Zs = np.concatenate([Zs, -Zs])

        if not antithetic: Zs = rng.standard_normal(N)

        if Zs.size < N:  # if N is odd, add one extra draw
            Zs = np.concatenate([Zs, rng.standard_normal(1)])
        
        r = float(self.r); q = float(self.q); vol = float(self.vol)
        S0 = float(self.spot); K = float(instrument.strike)
        disc = math.exp(-r * T)
        mu = (r - q - 0.5 * vol * vol) * T
        sig = vol * math.sqrt(T)
        payoffs = []

        for Z in Zs:
            ST = S0 * math.exp(mu + sig * Z)
            if instrument.option_type == QLOption.Call:
                payoff = max(ST - K, 0.0)
            else:
                payoff = max(K - ST, 0.0)
            payoffs.append(payoff)
        mean_payoff = sum(payoffs) / N
        var_payoff = (sum((x - mean_payoff)**2 for x in payoffs) / (N-1)) if N > 1 else 0.0
        price = disc * mean_payoff
        se = disc * math.sqrt(var_payoff / N)
        return price, se
    
    def delta(self, instrument, num_paths, bump=0.01, seed=None, antithetic=True, **kwargs):
        '''Finite-difference Delta: (P(S0+bump) - P(S0-bump)) / (2*bump).'''
        S0_orig = float(self.spot)
        b = 0.01 * S0_orig if (bump is None) else float(bump)
        try:
            self.spot = S0_orig + b
            up_price, _ = self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)
            self.spot = S0_orig - b
            dn_price, _= self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)
        finally:
            self.spot = S0_orig
        return (up_price - dn_price ) / (2.0 * b)
    
    def gamma(self, instrument, num_paths, bump=0.01, seed=None, antithetic=True, **kwargs):
        """Central-difference gamma: (P(S0+b) - 2*P(S0) + P(S0-b)) / b**2."""
        S0_orig = float(self.spot)
        b = 0.01 * S0_orig if (bump is None) else float(bump)
        S0_up = S0_orig + b; S0_dn = S0_orig - b
        try:
            self.spot = S0_up
            up_price, _ = self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)
            self.spot = S0_orig
            mid_price, _ = self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)
            self.spot = S0_dn
            dn_price, _ = self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)
        finally:
            self.spot = S0_orig

        return (up_price - 2.0 * mid_price + dn_price) / (b * b)

    def vega(self, instrument, num_paths, vol_bump=0.01, seed=None, antithetic=True, **kwargs):
        """Central-difference vega: (P(σ+dv) - P(σ-dv)) / (2*dv)."""
        vol_orig = float(self.vol)
        try:
            self.vol = vol_orig + vol_bump
            up_price, _ = self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)

            self.vol = vol_orig - vol_bump
            dn_price, _ = self.price_and_se(instrument, num_paths=num_paths, seed=seed, antithetic=antithetic)
        finally:
            self.vol = vol_orig

        return (up_price - dn_price) / (2.0 * vol_bump)
        
            
