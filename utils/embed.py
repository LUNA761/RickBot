"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

# <--- Imports --->

import discord


class Embed:
    # The init function
    def __init__(self, title: str = "", description: str = "", url: str = "", colour: int = 0x2f3136, timestamp=None,
                 thumbnail: str = None, image: str = None, author: dict = None, footer: dict = None):

        # Create the embed object and add the basic information
        self.embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            colour=discord.Colour(colour),
            timestamp=timestamp
        )

        # If the thumbnail is provided
        if thumbnail is not None:
            # Set the thumbnail as the url provided
            self.embed.set_thumbnail(url=thumbnail)

        # If the image is provided
        if image is not None:
            # Set the image as the url provided
            self.embed.set_image(url=image)

        # If the author is provided
        if author is not None:
            # Set the author as the name, url and icon_url provided
            self.embed.set_author(name=author["name"], url=author["url"], icon_url=author["icon"])

        # If the footer is provided
        if footer is not None:
            # Set the footer as the text and icon_url provided
            self.embed.set_footer(text=footer["text"], icon_url=footer["icon"])

    # The add fields function
    def add_fields(self, fields):
        # For each field in the list of fields
        for field in fields:
            # Add the field name and value to the embed
            self.embed.add_field(name=field["name"], value=field["value"])

    # The raw function
    def raw(self, data: dict = None):
        return self.embed
