import datetime

import discord
from discord.ext import commands

from utils import Confirm


class Context(commands.Context):
    """
    Custom context class.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def now(self) -> datetime.datetime:
        return self.message.created_at

    @property
    def unix(self) -> int:
        return int(self.message.created_at.timestamp())

    def embed(self, **kwargs):
        kwargs.setdefault("color", self.bot.color)
        return discord.Embed(**kwargs)

    async def reply(self, *args, **kwargs):
        ref = self.message.to_reference(fail_if_not_exists=False)
        try:
            return await self.send(*args, reference=ref, **kwargs)
        except discord.HTTPException:
            return await self.send(*args, **kwargs)

    async def confirm(
        self,
        content: str,
        *,
        timeout: int = 45,
        reply: bool = False,
        delete_after: bool = False,
        **kwargs
    ) -> bool:
        view = Confirm(timeout=timeout)

        if reply:
            msg = await self.reply(content, view=view, **kwargs)
        else:
            msg = await self.send(content, view=view, **kwargs)

        await view.wait()

        if delete_after:
            await msg.delete()

        return view.value
