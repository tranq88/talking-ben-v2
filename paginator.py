import discord


class Paginator:
    """Pagination with embeds."""

    def __init__(self,
                 title: str,
                 url: str,
                 elements: list[str],
                 max_per_page: int,
                 extra_footer: str = '',
                 formatter: str = '',
                 body_header: str = ''):
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
            p.set_thumbnail(url=url)
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


class PaginatorButtons(discord.ui.View):
    """Paginator controls."""

    def __init__(self, paginator: Paginator, owner: discord.User):
        super().__init__(timeout=60)
        self.paginator = paginator
        self.owner = owner

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    @discord.ui.button(label='Prev', disabled=True)
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

    @discord.ui.button(label='Next')
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
