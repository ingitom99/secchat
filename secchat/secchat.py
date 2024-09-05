"""Reflex app"""

import os
from dotenv import load_dotenv
import reflex as rx

from .scraper import get_all_data_for_ticker
from .engines import (
    make_engines,
    save_index,
    get_indexed_tickers
)

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

class State(rx.State):
    """The app state."""

    ticker: str
    query: str
    response: str
    indexed_tickers: list[str] = get_indexed_tickers()

    def set_ticker(self, value: str):
        self.ticker = value.lower()

    def add_ticker(self):
        # Check if the ticker already exists
        if self.ticker.lower() in self.indexed_tickers:
            return None
        else:
            # Save the ticker to ./indexed.txt in a new line
            with open("./indexed.txt", "a", encoding="utf-8") as f:
                f.write(f"{self.ticker.lower()}\n")  # Add \n for new line

            get_all_data_for_ticker(self.ticker)
            save_index(self.ticker)
            self.indexed_tickers = get_indexed_tickers()
            self.engines = make_engines(self.indexed_tickers)

    def respond(self):
        engines = make_engines(self.indexed_tickers)
        response = engines[self.ticker].query(self.query)
        self.response = response.response

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(
                "SECchat - Explore the filings...",
                color="white",
                font_weight="bold",
                font_size="24px",
                padding_left="10px",
            ),
            rx.spacer(),
            rx.color_mode.button(),
        ),
        background_color="#ef233c",
        padding=10,
        width="100%",
        height="60px",
    )


def ticker() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(
                "Ticker",
                size="4",
                weight="bold",
            ),
            rx.hstack(
                rx.input(
                    placeholder="aapl",
                    radius="large",
                    color_scheme="gray",
                    on_change=State.set_ticker,
                ),
                rx.button(
                    "Submit",
                    color_scheme="gray",
                    radius="large",
                    on_click=State.add_ticker,
                ),
            ),
        ),
        width="100%",
    )

def question() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(
                "Ask a question...",
                size="4",
                weight="bold",
            ),
            rx.text_area(
                placeholder="what was the 2021 revenue?",
                radius="large",
                color_scheme="gray",
                on_change=State.set_query,
            ),
            rx.button(
                "Submit",
                color_scheme="gray",
                radius="large",
                on_click=State.respond,
            )
        )
    )

def response() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(
                "Response:",
                size="4",
                weight="bold",
            ),
            rx.blockquote(
                State.response,
                color="black",
                font_size="16px"
            )
        )
    )

def qa_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            ticker(),
            question(),
            response(),
            spacing="6",
        )
    )

def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.vstack(
        navbar(),
        qa_page(),
        spacing="6",
        width="100%",
        align_items="center",
    )

app = rx.App()
app.add_page(index)
