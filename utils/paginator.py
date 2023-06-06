import discord
from datetime import datetime
from typing import Any


class Paginator:
    """Pagination with embeds."""
    # TODO: abstract this class way more
    def __init__(self,
                 title: str,
                 thumbnail_url: str,
                 elements: list[str],
                 max_per_page: int,
                 author: dict = None,
                 formatter: str = '',
                 body_header: str = '',
                 image_urls: list[str] = None,
                 extra_footer: str = '',
                 timestamps: list[datetime] = None):
        """
        Split the strings in <elements> into pages,
        where each page has at most <max_per_page> strings.
        """
        partitions = [
            elements[i:i+max_per_page]
            for i in range(0, len(elements), max_per_page)
        ]

        for i, p in enumerate(partitions):
            partitions[i] = '\n'.join(p)

        self.pages = [
            discord.Embed(
                title=title,
                description=f'{formatter}{body_header}{partition}{formatter}',
                color=discord.Color.from_rgb(181, 142, 101)
            )
            for partition in partitions
        ]

        for i, p in enumerate(self.pages):
            if author:
                p.set_author(
                    name=author['name'],
                    url=author['url'],
                    icon_url=author['icon_url']
                )
            if image_urls:
                # this is error prone - IndexError is raised if
                # len(self.pages) != len(image_urls)
                p.set_image(url=image_urls[i])
            if timestamps:
                # error prone for the same reason above
                p.timestamp = timestamps[i]

            p.set_thumbnail(url=thumbnail_url)
            p.set_footer(text=f'Page {i+1} of {len(self)}{extra_footer}')

        self.current_index = 0

    def __len__(self) -> int:
        return len(self.pages)

    def current_page(self) -> discord.Embed:
        return self.pages[self.current_index]

    def next_page(self):
        self.current_index += 1

    def prev_page(self):
        self.current_index -= 1

    def goto_page(self, index: int):
        self.current_index = index


class EmbedPaginator(Paginator):
    """Pagination with embeds"""
    def __init__(self, pages: list[Any]):
        self.pages = pages
        self.current_index = 0


class PaginatorButtons(discord.ui.View):
    """Paginator controls."""

    def __init__(self, paginator: Paginator, owner: discord.User):
        super().__init__(timeout=60)
        self.paginator = paginator
        self.owner = owner

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    @discord.ui.button(label='◂', disabled=True)
    async def prev_page(self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button):
        if interaction.user != self.owner:
            return

        self.paginator.prev_page()
        self.next_page.disabled = False

        if self.paginator.current_index == 0:
            button.disabled = True

        await interaction.response.edit_message(
            embed=self.paginator.current_page(),
            view=self
        )

    @discord.ui.button(label='▸')
    async def next_page(self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button):
        if interaction.user != self.owner:
            return

        self.paginator.next_page()
        self.prev_page.disabled = False

        if self.paginator.current_index == len(self.paginator) - 1:
            button.disabled = True

        await interaction.response.edit_message(
            embed=self.paginator.current_page(),
            view=self
        )
