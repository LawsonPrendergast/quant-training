import math
import random
from QuantLib import Date, Option, Actual365Fixed
from ql_wrapper.models import MonteCarloModel
from ql_wrapper.instruments import EuropeanOption

st = 100.0
K = 100.0
r =0.01
sigma = 0.20
expiry = Date(16, 7, 2026)

day_count = Actual365Fixed()
T = day_count.yearFraction(Date().todaysDate(), expiry)
print(f"Time to expiry T = {T:.4f} years")

Z = random.gauss(0,1)
ST = st * math.exp((r - .5 * sigma**2)*T + sigma * math.sqrt(T) * Z)

call_payoff = max(ST -K, 0)
put_payoff = max(K-ST, 0)
forward_payoff = ST-K

print(f"simulated ST = {ST:.4f}")
print(f"cALL - pUT Payoff = {call_payoff-put_payoff:.4f}")
print(f"forwad payoff = {forward_payoff:.4f}")

