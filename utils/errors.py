"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

import discord
from discord.ext import commands

import traceback
import sys
import logging

from .messages import cb_reply

ignored = (commands.CommandNotFound, )
log = logging.getLogger("rickbot")


async def handle_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return

    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.MemberNotFound):
        await cb_reply(ctx, "Member not found.")

    elif isinstance(error, commands.MissingPermissions):
        await cb_reply(ctx, "You can't do this.")

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} cannot be used in Private Messages.')
        except discord.HTTPException:
            pass

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.reply("Please provide all the required arguments when using this command.", mention_author=False)

    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        log.exception(f"{ctx.author} caused an error in {ctx.command}")  # exc_info=error
        # critical(error, luna=True)
