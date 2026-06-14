import math

from blurp.games.state import Answer
from blurp.games.whatnum.game import BinarySearch


def test_expected_guess_count():
    for low, high in [(1, 1), (1, 2), (1, 100), (1, 1024), (5, 5)]:
        bs = BinarySearch(low, high)
        n = high - low + 1
        assert bs.expected_guess_cnt == math.floor(math.log2(n)) + 1


def test_target_within_range():
    for _ in range(50):
        bs = BinarySearch(1, 100)
        assert 1 <= bs.target <= 100


def test_terminate_sets_status():
    bs = BinarySearch(1, 100)
    assert bs.status == Answer.NOT_ANSWERED

    bs.terminate(True)
    assert bs.status == Answer.ANSWERED_CORRECT

    bs.terminate(False)
    assert bs.status == Answer.ANSWERED_WRONG
