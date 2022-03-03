"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

import logging
import os
import json
from typing import Optional
from configparser import ConfigParser

import discord
from discord.ext import commands

from utils import format_time, plural, handle_error

from .context import Context

allowed_mentions = discord.AllowedMentions.none()
allowed_mentions.users = True

log = logging.getLogger("rickbot")

config = ConfigParser()
config.read('./rickconfig.ini')


class RickBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            strip_after_prefix=True,
            allowed_mentions=allowed_mentions,
            intents=discord.Intents.all(),
            help_command=HelpCommand()
        )

        self.color = int(config.get("RICK", "color"), 16)
        self.dot: str = config.get("EMOJIS", "wdot")

        self.loaded = {
            "cogs": [],
            "features": []
        }

        self.setup()

    def setup(self):
        self.load_extension("internal.cogs")

        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}")
                self.loaded["cogs"].append(file[:-3])

        for file in os.listdir("./features"):
            if file.endswith(".py"):
                self.load_extension(f"features.{file[:-3]}")
                self.loaded["features"].append(file[:-3])

        self.config = config

    def run(self):
        super().run(self.config.get("RICK", "token"))

    # Events
    async def on_ready(self):
        print(f"Logged in as {self.user}.")

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot or message.guild is None or message.webhook_id:
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        await handle_error(ctx, error)
        '''
        ignore = (commands.CommandNotFound,)
        if isinstance(error, ignore):
            return
        else:
            log.exception(f"{ctx.author} caused an error in {ctx.command}", exc_info=error)
            await ctx.reply(f"```py\n{type(error).__name__}: {error}```")
        '''

    async def close(self):
        await self.session.close()
        await super().close()


def get_prefix(bot, message):
    return commands.when_mentioned_or(config.get("RICK", "prefix"))(bot, message)


class HelpCommand(commands.HelpCommand):
    @property
    def clean_prefix(self) -> str:
        return self.context.clean_prefix

    @staticmethod
    def code_block(text: str) -> str:
        return f"`{text}`"

    @staticmethod
    def command_cooldown(command: commands.Command) -> Optional[str]:
        result = []

        cdm: commands.CooldownMapping = getattr(command, "_buckets")
        cd: commands.Cooldown = getattr(cdm, "_cooldown")
        if cdm and cd:
            bucket = (
                f"per {cdm.type.name}" if cdm.type != commands.BucketType.default else "globally"  # type: ignore
            )
            result.append(
                f'**Cooldown:** {plural(cd.rate, "time")} every '
                f"{format_time(cd.per, short=False)} ({bucket})"
            )

        max_conc: commands.MaxConcurrency = getattr(command, "_max_concurrency")
        if max_conc:
            bucket = (
                f"per {max_conc.per.name}"  # type: ignore
                if max_conc.per != commands.BucketType.default
                else "globally"
            )
            result.append(
                f'**Max Concurrency:** {plural(max_conc.number, "running instance")} ({bucket})'
            )

        if result:
            return "\n".join(result)

    def get_command_name(self, command):
        if not command.parent:
            return f"`{self.clean_prefix}{command.name}`"
        else:
            return f"`{self.clean_prefix}{command.parent} {command.name}`"

    def get_command_signature(self, command):
        if not command.signature and not command.parent:
            return f"`{self.clean_prefix}{command.name}`"
        elif command.signature and not command.parent:
            return f"`{self.clean_prefix}{command.name} {command.signature}`"
        elif not command.signature and command.parent:
            return f"`{self.clean_prefix}{command.parent} {command.name}`"
        else:
            return f"`{self.clean_prefix}{command.parent} {command.name} {command.signature}`"

    async def send_bot_help(self, cogs):
        bot = self.context.bot
        embed = discord.Embed(title=config.get("RICK", "name"), color=bot.color)
        blacklist = json.loads(config.get("RICK", "help_blacklist"))
        for cog in cogs.keys():
            if (
                getattr(cog, "qualified_name", None)
                and getattr(cog, "_hide_from_help", False) is not True
                and cog.qualified_name.lower() not in blacklist
            ):
                embed.add_field(
                    name=cog.qualified_name,
                    value=f"{bot.dot} `{self.clean_prefix}help {cog.qualified_name.lower()}`",
                    inline=False,
                )
        await self.context.reply(embed=embed)

    async def send_command_help(self, command):
        bot = self.context.bot
        embed = discord.Embed(title=self.get_command_name(command), color=bot.color)
        if self.get_command_name(command) != self.get_command_signature(command):
            embed.add_field(name="Usage:", value=self.get_command_signature(command), inline=False)
        if command.help or command.brief:
            embed.add_field(name="Description:", value=command.help or command.brief, inline=False)
        if command.aliases:
            embed.add_field(
                name="Aliases:",
                value=", ".join(self.code_block(alias) for alias in command.aliases),
                inline=False,
            )
        if cd := self.command_cooldown(command):
            embed.add_field(name="Rate Limits:", value=cd, inline=False)
        await self.context.reply(embed=embed)

    async def send_group_help(self, group):
        bot = self.context.bot
        formatted = [self.code_block(c.name) for c in group.commands]
        embed = discord.Embed(
            title=self.get_command_name(group),
            color=bot.color,
            description=", ".join(formatted),
        )
        if group.help or group.brief:
            embed.add_field(name="Description:", value=group.help or group.brief, inline=False)
        if group.aliases:
            embed.add_field(
                name="Aliases:",
                value=", ".join(self.code_block(alias) for alias in group.aliases),
                inline=False,
            )
        if cd := self.command_cooldown(group):
            embed.add_field(name="Rate Limits:", value=cd, inline=False)
        await self.context.reply(embed=embed)

    async def send_cog_help(self, cog):
        bot = self.context.bot
        cog_commands = ", ".join(self.code_block(c) for c in cog.get_commands()) or "No Commands."
        embed = discord.Embed(
            title=f"**{cog.qualified_name}**", color=bot.color, description=cog_commands
        )
        await self.context.reply(embed=embed)

    async def send_error_message(self, error):
        bot = self.context.bot
        embed = discord.Embed(description=f"**Error:** `{str(error)}`", color=bot.color)
        await self.context.reply(embed=embed)
