from typing import Any, Mapping, TypeAlias

import discord

# XXX(Nic): To make it easier to transition to the `State` dataclass if you
# decide to follow through with that.
State: TypeAlias = Mapping[str, Any]


def get_current_image(game_state: State) -> str:
    if game_state["game_over"]:
        return "jumpscare.webp"
    elif not game_state["camera_on"]:
        if game_state["door_closed"]:
            return "closedDoor.webp"
        elif game_state["light_on"]:
            if game_state["enemy_position"] in [
                "left-hall",
                "right-hall",
                "door",
            ]:
                return "lightE.webp"
            else:
                return "light.webp"
        else:
            return "default.webp"
    else:
        camera_map = {
            1: ("1M.webp", "main-stage"),
            2: ("2S.webp", "side-stage"),
            3: ("3K.webp", "kitchen"),
            4: ("4D.webp", "dining"),
            5: ("5R.webp", "right-hall"),
            6: ("6L.webp", "left-hall"),
        }

        prefix, pos = camera_map.get(
            game_state["current_camera"],
            ("1M.webp", "main-stage"),
        )

        if game_state["enemy_position"] == pos:
            return prefix.replace(".webp", "E.webp")
        else:
            return prefix


def create_embed(game_state: State) -> tuple[discord.Embed, str]:
    embed = discord.Embed(
        title="🎮 Five Nights at Alice's",
        color=0x8B0000 if game_state["game_over"] else 0x1F1F23,
    )

    if game_state["won"]:
        embed.add_field(
            name="🎉 VICTORY!", value="You survived all nights!", inline=False
        )
    elif game_state["game_over"]:
        embed.add_field(
            name="💀 GAME OVER",
            value=f"Survived Night {game_state['night']}, Hour {game_state['hour']}",
            inline=False,
        )
    else:
        embed.add_field(
            name="📊 Status",
            value=f"Night {game_state['night']}/{game_state['max_nights']} | Hour {game_state['hour']}/6 | Power {game_state['power']}%",
            inline=False,
        )
        embed.add_field(
            name="Systems",
            value=("🚪 CLOSED" if game_state["door_closed"] else "🚪 OPEN")
            + " | "
            + ("💡 ON" if game_state["light_on"] else "💡 OFF"),
            inline=False,
        )

    image_file = get_current_image(game_state)
    embed.set_image(url=f"attachment://{image_file}")
    return embed, image_file
