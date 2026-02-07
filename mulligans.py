from analysis import simulate_mulligans, simulate_early_game


def run_mulligan_simulation(deck, iterations=10_000):
    """
    Runs all mulligan-related simulations ONCE.
    This function is intentionally expensive and user-triggered.
    """

    mulligans = simulate_mulligans(deck, iterations=iterations)
    early_game = simulate_early_game(deck, iterations=iterations)

    return {
        "iterations": iterations,
        "mulligans": mulligans,
        "early_game": early_game,
        "note": (
            "These results are based on Monte Carlo simulations. "
            "Small variance is expected between runs."
        )
    }
