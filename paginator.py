import discord


class Paginator:
    """Pagination with embeds."""

    def __init__(self, elements: list[str], max_per_page):
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
                title='Tags for Goldfish Gang',
                description=partition,
                color=discord.Color.from_rgb(181, 142, 101)
            )
            for partition in partitions
        ]
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
