from discord import ApplicationContext


async def sendError(ctx: ApplicationContext, msg: str = "There's an error"):
    await ctx.respond(msg, ephemeral=True)
