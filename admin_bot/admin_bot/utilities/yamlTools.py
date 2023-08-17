# Tools for yaml stuff

import logging
import discord.utils
import yaml


def getSuggestion(roles) -> str:
    suggestions = []

    with open("admin_bot/resources/suggestions.yaml", "r") as file:
        all_sug = yaml.safe_load(file)

        for role in roles:
            if role == "@everyone":
                role = "everyone"

            if role in all_sug.keys():
                suggestions += all_sug[role]

                logging.debug(f"Trying to load {role} found {all_sug[role]} in {file}.")

    return suggestions
