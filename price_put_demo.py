import math
from QuantLib import Date, Option, Actual365Fixed
from ql_wrapper.models import BlackScholesModel, MonteCarloModel
from ql_wrapper.instruments import EuropeanOption




St = 100.0
K = 100.0
r = 0.01
sigma = 0.2
expiry = Date(15,7,2026)
day_count = Actual365Fixed()

T = day_count.yearFraction(Date().todaysDate(), expiry)
print("expiry =", expiry, "   type:", type(expiry))
put = EuropeanOption(K, expiry, Option.Put)
bs = BlackScholesModel(St,K,r, sigma)

put_price = bs.price(put)
mc_model = MonteCarloModel(St, r, sigma, num_paths=50000)
mc_put_price = mc_model.price(put)
print(f"Put Price = {put_price:.4f}")
print(f"monte carlo put price = {mc_put_price}")





