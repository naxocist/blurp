import asyncio
from typing import Callable

from discord import ApplicationContext

from blurp.ui.embeds import make_timer_embed


async def count_down_timer(
    ctx: ApplicationContext,
    timeout: int,
    *,
    title_prefix: str = "Time left:",
    interval: int = 5,
    check_done: Callable | None = None,
):
    if timeout <= 0:
        raise Exception("timeout must be positive value!")

    timer_msg = await ctx.send(embed=make_timer_embed(title_prefix, timeout))
    while timeout > 0:
        await asyncio.sleep(1)
        timeout -= 1

        if timeout == 0:
            await timer_msg.delete()
            return

        elif timeout % interval == 0 or timeout <= 5:
            await timer_msg.edit(embed=make_timer_embed(title_prefix, timeout))

        if check_done and check_done():
            if timeout > 0:
                await timer_msg.delete()
            return
