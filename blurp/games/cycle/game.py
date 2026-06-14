import asyncio
import random
from typing import List

from discord import Color, Embed, Member

from blurp.games.state import Answer, registry
from blurp.models.models import AnimeFull


class CycleClass:
    # time limit in seconds
    join_timeout = 20
    pick_timeout = 180
    delay_before_turn = 10
    turn_timeout = 60

    phases = ["lobby", "picking", "turns"]

    def __init__(self):
        registry.track(self)

        self.players: List[Member] = []
        self.targets: dict[Member, Member] = {}
        self.given_by: dict[Member, Member] = {}
        self.player_animes: dict[Member, AnimeFull] = {}
        self.player_count = 0

        self.players_pick_event: dict[Member, asyncio.Event] = {}
        self.players_picked: List[Member] = []

        self.turn_done: dict[Member, int] = {}
        self.status = Answer.NOT_ANSWERED
        self.answered_event = asyncio.Event()

        self.active_player_index = 0
        self.phase_index = 0
        self.round = 1
        self.done_players: List[Member] = []

    def add_player(self, player: Member):
        self.player_count += 1
        self.players.append(player)
        registry.bind(player, self)

    def get_pick_status(self):
        pick_status = ", ".join(
            [
                f"{player.mention} {'✅' if player in self.players_picked else '❌'}"
                for player in self.players
            ]
        )
        return pick_status

    def add_picked(self, player: Member):
        self.players_pick_event[player].set()
        self.players_picked.append(player)

    # shuffle and find derangements of players, then assign players to each other
    def random_targets(self):
        random.shuffle(self.players)
        pairs = [i for i in range(self.player_count)]

        # Expected time complexity: ~ O(n)*e
        while True:
            random.shuffle(pairs)
            if all(pairs[i] != i for i in range(len(pairs))):
                break

        for idx, player in enumerate(self.players):
            self.targets[player] = self.players[pairs[idx]]
            self.given_by[self.players[pairs[idx]]] = player

    def current_player(self) -> Member:
        return self.players[self.active_player_index]

    def advance_player(self):
        self.active_player_index += 1
        self.active_player_index %= self.player_count

        if self.active_player_index == 0:
            self.round += 1

    def add_done(self, player: Member):
        self.done_players.append(player)

    def advance_phase(self):
        self.phase_index += 1

    def current_phase(self) -> str:
        return CycleClass.phases[self.phase_index]

    def leaderboard(self) -> Embed:
        description = ""
        for rank, player in enumerate(self.done_players, start=1):
            anime = self.player_animes[player]
            giver = self.given_by[player]
            description += f"**#{rank}**: {player.mention} **Round {self.turn_done[player]}**\n[{anime.title}]({anime.url}) ❮❮ {giver.mention}\n"

        if not description:
            description = "No one's here..."
        return Embed(
            title=".⋅˚₊‧ 🜲Leaderboard ‧₊˚ ⋅",
            description=description,
            color=Color.gold(),
        )

    def clean(self):
        registry.remove(self)
