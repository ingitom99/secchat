"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import os

import reflex as rx
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from .secscraper import get_all_data_for_ticker
from .secagent import make_agent

agent = make_agent(
    "./data/TEST",
    openai_api_key
    )

class State(rx.State):
    """The app state."""

    ticker: str
    query: str
    response: str
    agent

    def change_agent(self):
        get_all_data_for_ticker(self.ticker)
        self.agent = make_agent(
            f"./data/{self.ticker}",
            openai_api_key
            )

    def respond(self):
        response = self.agent.query(self.query)
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
                    placeholder="APPL",
                    radius="large",
                    color_scheme="gray",
                    on_change=State.set_ticker,
                ),
                rx.button(
                    "Submit",
                    color_scheme="gray",
                    radius="large",
                    on_click=State.change_agent,
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
