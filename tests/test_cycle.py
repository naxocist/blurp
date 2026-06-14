from blurp.games.cycle.game import CycleClass


class FakePlayer:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return self.name


def make_game(player_count: int) -> CycleClass:
    game = CycleClass()
    for i in range(player_count):
        game.add_player(FakePlayer(f"p{i}"))
    return game


def test_random_targets_is_derangement():
    for n in range(2, 8):
        game = make_game(n)
        game.random_targets()

        for player in game.players:
            assert game.targets[player] is not player

        assert set(game.targets.values()) == set(game.players)

        for player in game.players:
            target = game.targets[player]
            assert game.given_by[target] is player

        game.clean()
