from QuantLib import Date, Option
from ql_wrapper.instruments import EuropeanOption
from ql_wrapper.models import MonteCarloModel, BlackScholesModel

# Instrument
expiry = Date(15, 7, 2026)
opt = EuropeanOption(100, expiry, Option.Call)

# Models
S0, r, sigma = 100.0, 0.01, 0.20
bs = BlackScholesModel(S0, 100, r, sigma)

# Show the “true” analytic reference
bs_price = bs.price(opt)
print(f"Black–Scholes price (reference): {bs_price:.4f}")

# Try different path counts
for N in [1_000, 5_000, 10_000, 50_000]:
    mc = MonteCarloModel(S0, r, sigma, num_paths=N)
    price, se = mc.price_and_se(opt)  # uses your new method
    print(f"N={N:>6}  MC Price = {price:.4f}  SE = {se:.4f}  95% CI ≈ [{price-1.96*se:.4f}, {price+1.96*se:.4f}]")