import discord
from discord.ext.commands import Context


class Paginator:
    """Pagination with embeds."""
    def __init__(self, pages: list[discord.Embed], show_index: bool = True):
        self.pages = pages

        for i, p in enumerate(self.pages):
            if show_index and p.footer.text:
                # put the page number in front of any footer the embed has
                new_footer = f'Page {i+1} of {len(self)} | {p.footer.text}'
            elif show_index:
                new_footer = f'Page {i+1} of {len(self)}'
            elif p.footer.text:
                new_footer = p.footer.text
            else:
                new_footer = None

            p.set_footer(text=new_footer)

        self.current_index = 0

    def __len__(self) -> int:
        return len(self.pages)

    def current_page(self) -> discord.Embed:
        return self.pages[self.current_index]

    def next_page(self):
        self.current_index += 1

    def prev_page(self):
        self.current_index -= 1

    def first_page(self):
        self.current_index = 0

    def last_page(self):
        self.current_index = len(self) - 1

    def goto_page(self, index: int):
        self.current_index = index


class PaginatorButtons(discord.ui.View):
    """Paginator controls."""

    def __init__(self, paginator: Paginator, owner: discord.User):
        super().__init__(timeout=60)
        self.paginator = paginator
        self.owner = owner

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    @discord.ui.button(label='◂◂', disabled=True)
    async def first_page(self,
                         interaction: discord.Interaction,
                         button: discord.ui.Button):
        if interaction.user != self.owner:
            return

        self.paginator.first_page()
        self.next_page.disabled = False
        self.last_page.disabled = False

        button.disabled = True
        self.prev_page.disabled = True

        await interaction.response.edit_message(
            embed=self.paginator.current_page(),
            view=self
        )

    @discord.ui.button(label='◂', disabled=True)
    async def prev_page(self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button):
        if interaction.user != self.owner:
            return

        self.paginator.prev_page()
        self.next_page.disabled = False
        self.last_page.disabled = False

        if self.paginator.current_index == 0:
            button.disabled = True
            self.first_page.disabled = True

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
        self.first_page.disabled = False

        if self.paginator.current_index == len(self.paginator) - 1:
            button.disabled = True
            self.last_page.disabled = True

        await interaction.response.edit_message(
            embed=self.paginator.current_page(),
            view=self
        )

    @discord.ui.button(label='▸▸')
    async def last_page(self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button):
        if interaction.user != self.owner:
            return

        self.paginator.last_page()
        self.prev_page.disabled = False
        self.first_page.disabled = False

        button.disabled = True
        self.next_page.disabled = True

        await interaction.response.edit_message(
            embed=self.paginator.current_page(),
            view=self
        )


async def reply_paginator(paginator: Paginator,
                          ctx: Context,
                          content: str = None):
    """Reply to <ctx> with <p>."""
    if len(paginator) == 1:  # send without buttons
        await ctx.reply(
            content=content,
            embed=paginator.current_page(),
            mention_author=False
        )
    else:
        view = PaginatorButtons(paginator=paginator, owner=ctx.author)
        view.message = await ctx.reply(
            content=content,
            embed=paginator.current_page(),
            view=view,
            mention_author=False
        )
