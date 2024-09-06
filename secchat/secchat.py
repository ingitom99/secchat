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

    def update_ticker(self, form_data: dict):
        
        self.ticker = form_data["ticker"].lower()

        if self.ticker in self.indexed_tickers:
            return None
        
        else:
            # Save the ticker to ./indexed.txt in a new line
            with open("./indexed.txt", "a", encoding="utf-8") as f:
                f.write(f"{self.ticker.lower()}\n")  # Add \n for new line

            get_all_data_for_ticker(self.ticker)
            save_index(self.ticker)
            self.indexed_tickers = get_indexed_tickers()
            self.engines = make_engines(self.indexed_tickers)
        

    def respond(self, form_data: dict):
        self.query = form_data["query"]
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
        width="100%",
        padding=10,
        height="60px"
    )


def ticker() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.heading(
                "Ticker",
                size="4",
                weight="bold",
            ),
            rx.hstack(
                rx.input(
                    name="ticker",
                    type="text",
                    placeholder=State.ticker,
                    radius="large"
                ),
                rx.button(
                    "Submit",
                    type="submit",
                    radius="large"
                ),
            ),
            align="stretch"
        ),
        on_submit=State.update_ticker
    )

def question() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.heading(
                "Ask a question...",
                size="4",
                weight="bold",
            ),
            rx.text_area(
                placeholder="what was the 2021 revenue?",
                name="query",
                radius="large"
            ),
            rx.button(
                "Submit",
                type="submit",
                radius="large"
            ),
            align="stretch"
        ),
        on_submit=State.respond
        
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
    return rx.box(
        rx.vstack(
            ticker(),
            question(),
            response(),
            spacing="6",
            align="stretch"
        ),
        width="50%"
    )

def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        rx.vstack(
            navbar(),
            qa_page(),
            spacing="6",
            width="100%",
            align_items="center",
        ),
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="iris",
        background_color="iris",
    )
)
app.add_page(index)
