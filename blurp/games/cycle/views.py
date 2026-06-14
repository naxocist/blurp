import discord
from discord import Interaction, Member
from discord.ui import Button, View


class InviteView(View):
    def __init__(self, cycle_object, timeout):
        super().__init__(timeout=timeout, disable_on_timeout=True)
        self.cycle_object = cycle_object
        self.is_terminated = False
        self.terminator = None

    @discord.ui.button(label="join", style=discord.ButtonStyle.green, emoji="🤓")
    async def join(self, _, interaction: Interaction):
        if not isinstance(interaction.user, Member):
            return

        member: Member = interaction.user
        if member in self.cycle_object.players:
            await interaction.response.send_message(
                "You are already in the game!", ephemeral=True
            )
            return

        self.cycle_object.add_player(member)
        await interaction.response.send_message(f"{member.mention} joined!")

    @discord.ui.button(
        label="force start", style=discord.ButtonStyle.blurple, emoji="💀"
    )
    async def start(self, _, interaction: Interaction):
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="terminate", style=discord.ButtonStyle.red)
    async def terminate(self, _, interaction: Interaction):
        await interaction.response.defer()
        self.is_terminated = True
        self.terminator = interaction.user
        self.stop()


class TurnView(View):
    def __init__(self, is_last_player: bool):
        super().__init__()
        self.is_last_player = is_last_player
        self.is_terminated = False
        self.terminator = None

        next_player_button = Button(
            label="next player",
            style=discord.ButtonStyle.green,
            disabled=is_last_player,
        )
        next_player_button.callback = self.next_player
        self.add_item(next_player_button)

    async def next_player(self, interaction: Interaction):
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="terminate", style=discord.ButtonStyle.red)
    async def terminate(self, _, interaction: Interaction):
        await interaction.response.defer()
        self.is_terminated = True
        self.terminator = interaction.user
        self.stop()


class PickView(View):
    def __init__(self):
        super().__init__()
        self.is_terminated = False
        self.terminator = None

    @discord.ui.button(label="terminate", style=discord.ButtonStyle.red)
    async def terminate(self, _, interaction: Interaction):
        await interaction.response.defer()
        self.is_terminated = True
        self.terminator = interaction.user
        self.stop()
