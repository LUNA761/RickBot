"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

import discord
from discord.ext import commands

from .embed import Embed


async def cb_reply(ctx: commands.Context, content: str, mention: bool = False):
    return await ctx.message.reply(embed=Embed(description=f"`{content}`").raw(), mention_author=mention)


async def cb_reply_edit(msg: discord.Message, content: str, mention: bool = False):
    return await msg.edit(embed=Embed(description=f"`{content}`").raw())


async def cb_send(ctx: commands.Context, content: str, mention: bool = False):
    return await ctx.send(embed=Embed(description=f"`{content}`").raw(), mention_author=mention)


async def e_reply(ctx: commands.Context, content: str, mention: bool = False):
    return await ctx.message.reply(embed=Embed(description=content).raw(), mention_author=mention)


async def reply(ctx: commands.Context, content: str, mention: bool = False):
    return await ctx.message.reply(content, mention_author=mention)


async def send(ctx: commands.Context, content: str, mention: bool = False):
    return await ctx.send(content, mention_author=mention)
