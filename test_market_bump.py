from ql_wrapper.market import MarketParams
from ql_wrapper.models import BlackScholesModel
from ql_wrapper.instruments import Option
from QuantLib import Option as QLOption, Period, Months, Date, Settings

def test_market_bump_updates_price():
    Settings.instance().evaluationDate = Date.todaysDate()
    mat = Date().todaysDate() + Period(6, Months)
    mkt = MarketParams(spot=100, risk_free_rate=0.03, div_yield=0.0, vol=0.2)
    bs = BlackScholesModel(market=mkt)
    opt = Option(strike=100, maturity_date=mat, option_type=QLOption.Call)
    base_price = bs.price(opt)
    mkt.set_spot(105)
    bumped_price = bs.price(opt)
    assert bumped_price > base_price

