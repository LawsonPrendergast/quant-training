from QuantLib import Settings, Date, Period, Months, Option as QLOption
from ql_wrapper.market import MarketParams
from ql_wrapper.models import BlackScholesModel
from ql_wrapper.instruments import Option

def test_call_price_monotone_in_r_and_sigma():
    Settings.instance().evaluationDate = Date.todaysDate()
    mat = Date.todaysDate() + Period(6, Months)
    opt = Option(strike=100, maturity_date=mat, option_type=QLOption.Call)

    mkt = MarketParams(spot=100, risk_free_rate=0.02, div_yield=0.00, vol=0.20)
    bs  = BlackScholesModel(market=mkt)

    p0 = bs.price(opt)

    # r up -> call up
    mkt.set_rate(0.04)
    p_r_up = bs.price(opt)
    assert p_r_up > p0

    # sigma up -> call up
    mkt.set_vol(0.25)
    p_sigma_up = bs.price(opt)
    assert p_sigma_up > p_r_up