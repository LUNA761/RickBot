from typing import Optional

import discord
from discord.ext import commands

from .sources import PageSource


class Confirm(discord.ui.View):
    def __init__(self, timeout: int = 45):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, _button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        await self.disable_all(interaction)
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, _button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        await self.disable_all(interaction)
        self.stop()

    async def disable_all(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)


class PaginatedView(discord.ui.View):
    def __init__(self, source: PageSource, *, timeout: int = 60):
        super().__init__(timeout=timeout)
        self._source = source
        self.current_page = 0
        self._author_id: Optional[int] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self._author_id:
            await interaction.response.send_message("You can't do that.", ephemeral=True)
            return False
        return True

    async def send_initial_message(self, ctx: commands.Context):
        self._author_id = ctx.author.id
        page = await self._source.get_page(self.current_page)
        kwargs = await self._get_kwargs_from_page(page)
        return await ctx.reply(**kwargs)

    async def _get_kwargs_from_page(self, page) -> dict:
        value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
        kwargs: Optional[dict] = None
        if isinstance(value, dict):
            kwargs = value
        elif isinstance(value, str):
            kwargs = {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            kwargs = {"embed": value, "content": None}
        kwargs["view"] = self
        return kwargs

    async def show_page(self, page_number: int, interaction: discord.Interaction):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await interaction.response.edit_message(**kwargs)

    async def show_checked_page(self, page_number: int, interaction: discord.Interaction) -> None:
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None or max_pages > page_number >= 0:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number, interaction)
            elif page_number >= max_pages:
                await self.show_page(0, interaction)
            else:
                await self.show_page(max_pages - 1, interaction)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    @discord.ui.button(label="previous", style=discord.ButtonStyle.blurple)
    async def previous(self, _button: discord.ui.Button, interaction: discord.Interaction):
        await self.show_checked_page(self.current_page - 1, interaction)

    @discord.ui.button(label="stop", style=discord.ButtonStyle.red)
    async def stop_button(self, _button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="next", style=discord.ButtonStyle.blurple)
    async def next(self, _button: discord.ui.Button, interaction: discord.Interaction):
        await self.show_checked_page(self.current_page + 1, interaction)
