from QuantLib import Date, Period, Months, Option as QLOption
from ql_wrapper.market import MarketParams
from ql_wrapper.instruments import Option
from ql_wrapper.models import BlackScholesModel

def  test_american_price_higher_than_european():

    today = Date.todaysDate()
    mat = today + Period(6, Months)

    strike = 100.0
    mkt = MarketParams(spot=100, risk_free_rate=0.03, div_yield=0.01, vol=0.25)
    model = BlackScholesModel(market=mkt)

    euro = Option(strike=strike, maturity_date=mat, option_type=QLOption.Call)
    euro.style = "European"

    amer = Option(strike=strike, maturity_date=mat, option_type=QLOption.Call)
    amer.style = "American"

    p_euro = model.price(euro)
    p_amer = model.price(amer)
    

