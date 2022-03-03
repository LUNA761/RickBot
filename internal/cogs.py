"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

from configparser import ConfigParser
from git.repo.base import Repo
from os.path import exists
import configparser
import asyncio
import shutil
import uuid
import json
import traceback
import glob
import os

from discord.ext import commands
from discord.ext.commands import check

from utils import bot_owner, cb_reply, cb_reply_edit, rmtree_error


class CogInstaller(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="install")
    @check(bot_owner)
    async def _install(self, ctx, github_repo: str = None):
        if github_repo is None:
            await cb_reply(ctx, "You need to provide a repo to install")
            return

        repo_temp_uuid = uuid.uuid4()
        repo_path = f"./cache/{repo_temp_uuid}"

        async with ctx.typing():
            reply = await cb_reply(ctx, "Downloading...")
            Repo.clone_from(github_repo, repo_path)

        if not exists(f"{repo_path}/metadata.json"):
            await cb_reply_edit(reply, "This repo is not a cog/feature or it isn't formatted correctly.")
            await self.delete_repo(repo_path)
            return

        elif not exists(f"{repo_path}/cog.py") and not exists(f"{repo_path}/feature.py"):
            await cb_reply_edit(reply, "This repo is not a cog/feature or it isn't formatted correctly.")
            await self.delete_repo(repo_path)
            return

        with open(f"{repo_path}/metadata.json") as f:
            try:
                repo_metadata = json.load(f)
                f.close()
            except json.decoder.JSONDecodeError:
                f.close()
                await cb_reply_edit(reply, "The metadata cannot be decoded.")
                await self.delete_repo(repo_path)
                return

            except Exception as error:
                f.close()
                await cb_reply_edit(reply, "Something went wrong while reading the metadata, this is an error with me. Please see the console for more information.")
                print(traceback.format_exception(error))
                await self.delete_repo(repo_path)
                return

        try:
            for i in ["name", "raw_name", "author", "type"]:
                _ = repo_metadata[i]
            del _
        except KeyError:
            await cb_reply_edit(reply, "The metadata is not formatted correctly.")
            await self.delete_repo(repo_path)
            return

        async with ctx.typing():
            await cb_reply_edit(reply, f"Installing '{repo_metadata['name']}' By '{repo_metadata['author']}'")

            repo_installed = {
                "helpers": []
            }

            if "config" in repo_metadata:
                if not exists("./configs"):
                    os.mkdir("./configs")

                configp = ConfigParser()
                configp.read(f"./configs/{repo_metadata['raw_name']}.ini")
                for config_entry in repo_metadata["config"]:
                    try:
                        configp.add_section(config_entry.upper())
                    except configparser.DuplicateSectionError:
                        pass

                    for config_entry_data in repo_metadata["config"][config_entry]:
                        configp.set(config_entry.upper(), config_entry_data,
                                    repo_metadata["config"][config_entry][config_entry_data])

                with open(f"./configs/{repo_metadata['raw_name']}.ini", 'w+') as configfile:
                    configp.write(configfile)

            if exists(f"{repo_path}/helpers"):
                for helper in glob.glob(f"{repo_path}/helpers/*.py"):
                    shutil.move(helper, f"./helpers/{os.path.basename(helper)}")
                    repo_installed["helpers"].append(os.path.basename(helper)[:-3])

            if repo_metadata["type"] == "feature":
                shutil.move(f"{repo_path}/feature.py", f"./features/{repo_metadata['raw_name']}.py")
                try:
                    self.client.load_extension(f"features.{repo_metadata['raw_name']}")
                except:
                    await cb_reply_edit(reply, "A feature/cog with the same name has already been installed.")
                    await self.delete_repo(repo_path)
                    return
                repo_installed["cog/feature"] = repo_metadata["raw_name"]

            elif repo_metadata["type"] == "cog":
                shutil.move(f"{repo_path}/cog.py", f"./cogs/{repo_metadata['raw_name']}.py")
                try:
                    self.client.load_extension(f"cogs.{repo_metadata['raw_name']}")
                except:
                    await cb_reply_edit(reply, "A feature/cog with the same name has already been installed.")
                    await self.delete_repo(repo_path)
                    return
                repo_installed["cog/feature"] = repo_metadata["raw_name"]

            repo_install_info = "Helpers:\n"
            for helper in repo_installed["helpers"]:
                repo_install_info += f"- {helper}\n"
            repo_install_info += f"\nCog/Feature:\n- {repo_installed['cog/feature']}"

        await cb_reply_edit(reply, f"Installed '{repo_metadata['name']}' By '{repo_metadata['author']}'\n\nInstall information:\n{repo_install_info}")
        await self.delete_repo(repo_path)

    async def delete_repo(self, path: str):
        await asyncio.sleep(2)
        shutil.rmtree(path, onerror=rmtree_error)
        return


def setup(client):
    client.add_cog(CogInstaller(client))
