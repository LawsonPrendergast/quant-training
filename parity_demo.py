import math
from QuantLib import Date, Option, Actual365Fixed
from ql_wrapper.models import BlackScholesModel
from ql_wrapper.instruments import EuropeanOption

# --- Put-Call Parity Demonstration ---
st    = 100.0     # Spot price
K     = 100.0     # Strike price
r     = 0.01      # Risk-free rate (1%)
sigma = 0.20      # Volatility (20%)
expiry = Date(15, 7, 2026)
day_count = Actual365Fixed()
T = day_count.yearFraction(Date().todaysDate(), expiry)

# Build instruments
call = EuropeanOption(K, expiry, Option.Call)
put  = EuropeanOption(K, expiry, Option.Put)

# Build the model
bs = BlackScholesModel(st, K, r, sigma)

# Compute prices
call_price = bs.price(call)
put_price  = bs.price(put)

# Check parity
lhs = call_price - put_price
rhs = st - K * math.exp(-r * T)

print(f"Call - Put = {lhs:.4f}")
print(f"st - K*exp(-rT) = {rhs:.4f}")
