from QuantLib import Settings, Date, Option as QLOption, Period, Months
from ql_wrapper.market import MarketParams
from ql_wrapper.models import BlackScholesModel
from ql_wrapper.instruments import Option

Settings.instance().evaluationDate = Date.todaysDate()
mat = Date().todaysDate() + Period(6, Months)

mkt = MarketParams(spot=100, risk_free_rate=0.03, div_yield=0.0, vol=0.20)
bs = BlackScholesModel(market=mkt)
opt = Option(strike=100, maturity_date=mat, option_type=QLOption.Call)

print(bs.price(opt))