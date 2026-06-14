from dataclasses import dataclass
from math import floor, log2
from random import randint

from discord import Color, Embed

from blurp.games.state import Answer


@dataclass(init=False)
class BinarySearch:
    """
    Expected Behavior:
        at any possible range [l, r]
        let n = r - l + 1 = number of elements
            let k = least possible integer, where 2^k >= n
            n = 2^k: worst case = log2(n) + 1 = k + 1
            n != 2^k: worse case = floor(log2(n)) + 1 = k + 1
    """

    def __init__(self, low: int, high: int):
        self.low, self.high = low, high
        self.target = randint(low, high)
        self.expected_guess_cnt = floor(log2(high - low + 1)) + 1
        self.guess_cnt = 0

        self.status = Answer.NOT_ANSWERED

    def terminate(self, success: bool):
        self.status = Answer.ANSWERED_CORRECT if success else Answer.ANSWERED_WRONG

    @staticmethod
    def fail_embed(target: str) -> Embed:
        return Embed(
            title="Failed",
            description=f"The number was **{target}**\nYou're not being optimal... You should've guessed it.\nMaybe look into [binary search](https://en.wikipedia.org/wiki/Binary_search)",
            color=Color.red(),
        )
