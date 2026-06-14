from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from discord import Member

if TYPE_CHECKING:
    from blurp.games.clues.game import ClueClass
    from blurp.games.cycle.game import CycleClass
    from blurp.games.whatnum.game import BinarySearch

    Game = CycleClass | ClueClass | BinarySearch


class Answer(Enum):
    NOT_ANSWERED = 0
    ANSWERED_WRONG = 1
    ANSWERED_CORRECT = 2


class GameRegistry:
    def __init__(self):
        self.games: list[Game] = []
        self.players: dict[Member, Game] = {}

    def __contains__(self, player: Member) -> bool:
        return player in self.players

    def track(self, game: Game) -> None:
        if game not in self.games:
            self.games.append(game)

    def bind(self, player: Member, game: Game) -> None:
        self.players[player] = game
        self.track(game)

    def get(self, player: Member) -> Game | None:
        return self.players.get(player)

    def remove(self, game: Game) -> None:
        self.games = [g for g in self.games if g is not game]
        self.players = {p: g for p, g in self.players.items() if g is not game}


registry = GameRegistry()
