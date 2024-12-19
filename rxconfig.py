import reflex as rx

config = rx.Config(
    app_name="poke_trivia",
    tailwind={
        "theme": {
            "extend": {},
        },
        "plugins": ["@tailwindcss/typography"],
    },
)