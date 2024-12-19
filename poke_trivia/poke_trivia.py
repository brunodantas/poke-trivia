import datetime
import re
from itertools import chain

import reflex as rx
import requests
from bs4 import BeautifulSoup

from rxconfig import config


class State(rx.State):
    """The app state."""

    title = ""
    image = ""
    content = ""

    def get_pokemon_url(self):
        response = requests.get(
            "https://bulbapedia.bulbagarden.net/wiki/"
            "List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        table_contents = (
            c or ""
            for c in chain.from_iterable(
                table.contents for table in soup.find_all("table")
            )
            if not c.string
        )
        urls = list(
            set(
                re.findall(
                    "(/wiki/.*_\(Pok%C3%A9mon\))",
                    " ".join(str(c) for c in table_contents),
                )
            )
        )
        today = datetime.datetime.today().date()
        url = urls[hash(today) % len(urls)]
        return url

    def get_pokemon_data(self):
        url = "https://bulbapedia.bulbagarden.net" + self.get_pokemon_url()
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        image_tag = soup.find_all("img")[2]
        self.image = image_tag["src"]
        self.title = " ".join(str(soup.find("h1").string).split()[:-1])
        tag = soup.find("h2", string="Trivia")
        content = []
        if tag:
            for c in tag.find_next_siblings():
                if c and c.name == "h2":
                    break
                content.append(str(c))
        self.content = "".join(content)
        self.content = self.content.replace(
            "/wiki/", "https://bulbapedia.bulbagarden.net/wiki/"
        )


@rx.page(on_load=State.get_pokemon_data)
def index() -> rx.Component:
    return rx.container(
        # rx.color_mode.button(position="top-right"),
        rx.heading("PokéTrivia"),
        rx.text("Daily Pokémon trivia, powered by Bulbapedia"),
        rx.separator(),
        rx.vstack(
            rx.spacer(spacing="5"),
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        State.title,
                    ),
                    rx.image(src=State.image),
                    align="center"
                ),
                rx.html(State.content, class_name="prose"),
                justify="center",
                min_height="85vh",
            ),
        ),
    )


app = rx.App()
app.add_page(index)
