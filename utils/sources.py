from __future__ import annotations

from typing import Any, List

import discord
from discord.ext.menus import ListPageSource


class PageSource(ListPageSource):
    def __init__(self, pages: List[Any], per_page: int = 1):
        super().__init__(pages, per_page=per_page)

    async def format_page(self, view: discord.ui.View, page: Any):
        return page
