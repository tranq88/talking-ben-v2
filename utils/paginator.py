import discord
from typing import Any


class Paginator:
    """Pagination with embeds."""
    def __init__(self, pages: list[discord.Embed], show_index: bool = True):
        # partitions = [
        #     elements[i:i+max_per_page]
        #     for i in range(0, len(elements), max_per_page)
        # ]

        # for i, p in enumerate(partitions):
        #     partitions[i] = '\n'.join(p)

        self.pages = pages

        # put the page number in front of any footer the embed has
        
        # for i, p in enumerate(self.pages):
        #     p.set_footer(
        #         text=(
        #             f'{f"Page {i+1} of {len(self)}" if show_index else ""}'
        #             f'{f" | {p.footer.text}" if p.footer.text and show_index else ""}'
        #         )
        #     )

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
