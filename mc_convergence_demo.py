from ql_wrapper.models import BlackScholesModel, MonteCarloModel
import numpy as np
import matplotlib.pyplot as plt

def mc_stats_vs_paths(mc_model, option_obj, Ns, bump=0.10):
    prices, ses, deltas = [], [], []
    for N in Ns:
        p, se = mc_model.price_and_se(option_obj, num_paths=N)
        d = mc_model.delta(option_obj, bump=bump, num_paths=N)
        prices.append(p); ses.append(se); deltas.append(d)
    return np.array(prices), np.array(ses), np.array(deltas)

def plot_convergence(mc_model, bs_model, option_obj, Ns, bump=0.10):
    true_price = bs_model.price(option_obj)
    true_delta = bs_model.greeks(option_obj)['delta']
    prices, ses, deltas = mc_stats_vs_paths(mc_model, option_obj, Ns, bump=bump)
    plt.figure(figsize=(8,5))
    plt.plot(Ns, prices, marker='o', label='MC Price')
    plt.fill_between(Ns, prices - 2*ses, prices + 2*ses, alpha=0.2, label="±2 SE")
    plt.axhline(true_price, linestyle='--', label = 'Analytic price')
    plt.xscale('log')
    plt.title('MC Convergence: Price vs Number of Paths')
    plt.xlabel('Number of paths (log scale)')
    plt.ylabel("Option price")
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8,5))
    plt.plot(Ns, deltas, marker="o", label="MC delta (FD)")
    plt.axhline(true_delta, linestyle="--", label="Analytic delta")
    plt.xscale("log")
    plt.title("MC Convergence: Delta vs Number of Paths")
    plt.xlabel("Number of paths (log scale)")
    plt.ylabel("Delta")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    from QuantLib import Date, Settings, Period, Months, Option

    # Evaluation date
    today = Date.todaysDate()
    Settings.instance().evaluationDate = today

    # Build a simple option object with required attributes
    class Opt: pass
    opt = Opt()
    opt.type = Option.Call
    opt.strike = 100.0
    opt.maturity = today + Period(6, Months)

    # Models
    bs = BlackScholesModel(spot=100.0, strike_price=opt.strike, risk_free_rate=0.03, volatility=0.20)
    mc = MonteCarloModel(spot=100.0, risk_free_rate=0.03, volatility=0.20, num_paths=10000)

    # Path counts to test
    Ns = np.array([500, 1000, 2000, 5000, 10000, 20000, 50000])

    # Run the convergence plots
    plot_convergence(mc, bs, opt, Ns, bump=0.10)
