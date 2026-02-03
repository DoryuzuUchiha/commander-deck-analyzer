from hypergeom import at_least, at_least_one

def land_consistency(deck):
    N = deck.library_size
    K = deck.land_count

    return {
        "P(2+ lands opening hand)": at_least(2, N, K, 7),
        "P(3+ lands by turn 3)": at_least(3, N, K, 9),
        "P(4+ lands by turn 4)": at_least(4, N, K, 10),
        "P(5+ lands by turn 5)": at_least(5, N, K, 11),
    }

def ramp_consistency(deck):
    N = deck.library_size
    K = deck.ramp_count

    return {
        "P(ramp in opening hand)": at_least_one(N, K, 7),
        "P(ramp by turn 2)": at_least_one(N, K, 8),
        "P(ramp by turn 3)": at_least_one(N, K, 9),
    }
