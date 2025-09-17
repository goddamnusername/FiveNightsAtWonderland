from __future__ import annotations

import asyncio
import os
import random
import time
from typing import Any, MutableMapping

import discord

from config import logger

from .enemy import EnemyAI
from .utils import create_embed
from .view import FNAFGameView


class FNAFDiscordGame:
    def __init__(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        active_games: MutableMapping[int, FNAFDiscordGame],
    ) -> None:
        self.channel = channel
        self.user = user
        self.active_games = active_games
        self.game_message: discord.Message | None = None
        self.view: FNAFGameView | None = None

        self.night = 1
        self.max_nights = 5
        self.hour = 0
        self.power = 100.0
        self.game_over = False
        self.won = False
        self.game_active = False
        self.hour_length = 60

        self.camera_on = False
        self.current_camera = 1

        self.enemy = EnemyAI()
        self.door_closed = False
        self.light_on = False

        self.last_power_drain = time.time()
        self.last_hour_update = time.time()
        self.last_update_time = 0.0
        self.game_task: asyncio.Task[None] | None = None

    @property
    def enemy_position(self) -> str:
        return self.enemy.position

    @property
    def enemy_at_door(self) -> bool:
        return self.enemy.at_door

    def get_game_state(self) -> dict[str, Any]:
        return {
            "game_over": self.game_over,
            "won": self.won,
            "night": self.night,
            "max_nights": self.max_nights,
            "hour": self.hour,
            "power": self.power,
            "camera_on": self.camera_on,
            "current_camera": self.current_camera,
            "enemy_position": self.enemy_position,
            "door_closed": self.door_closed,
            "light_on": self.light_on,
        }

    async def update_game_display(self, force: bool = False) -> None:
        now = time.time()
        if not force and now - self.last_update_time < 6:
            return
        self.last_update_time = now

        if not self.game_message:
            return

        embed, image_file = create_embed(self.get_game_state())
        assert self.view is not None
        self.view.update_buttons()
        file_path = f"assets/{image_file}"
        file = (
            discord.File(file_path, filename=image_file)
            if os.path.exists(file_path)
            else None
        )

        try:
            await self.game_message.edit(
                embed=embed, view=self.view, attachments=[file] if file else []
            )
        except Exception:
            logger.warning("Failed to update game message")

    def drain_power(self) -> None:
        now = time.time()
        if now - self.last_power_drain >= 5:
            self.last_power_drain = now
            drain = (
                0.5
                + (1 if self.door_closed else 0)
                + (0.5 if self.light_on else 0)
                + (0.5 if self.camera_on else 0)
            )
            self.power = max(0.0, self.power - drain)
            if self.power == 0:
                asyncio.create_task(self.power_outage())

    async def power_outage(self) -> None:
        self.door_closed = False
        self.light_on = False
        self.camera_on = False
        await self.update_game_display(force=True)
        await asyncio.sleep(1)
        await self.handle_game_over("power_outage")

    async def handle_game_over(self, reason: str) -> None:
        self.game_over = True
        self.game_active = False
        self.enemy.at_door = True
        await self.update_game_display(force=True)

    async def game_loop(self) -> None:
        while self.game_active and not self.game_over and not self.won:
            now = time.time()

            if now - self.last_hour_update >= self.hour_length:
                self.hour += 1
                self.last_hour_update = now
                if self.hour >= 6:
                    await self.next_night()
                    continue

            self.enemy.move_enemy(self.hour)
            self.drain_power()

            if (
                self.enemy_at_door
                and not self.door_closed
                and random.random() < 0.2
            ):
                await self.handle_game_over("door_attack")
                break

            await self.update_game_display()
            await asyncio.sleep(1)

        await self.update_game_display(force=True)

    async def next_night(self) -> None:
        if self.night >= self.max_nights:
            self.won = True
            self.game_active = False
            await self.update_game_display(force=True)
            return

        self.night += 1
        self.hour = 0
        self.power = 100
        self.enemy.reset()
        self.door_closed = False
        self.light_on = False

        assert self.game_message is not None
        await self.game_message.edit(
            embed=discord.Embed(
                title=f"🌙 Night {self.night - 1} Complete!",
                description="Prepare for the next night...",
                color=0xFFD700,
            ),
            view=None,
        )
        await asyncio.sleep(5)

        self.last_hour_update = time.time()
        await self.update_game_display(force=True)

    async def open_camera(self) -> None:
        self.camera_on = True

    async def switch_camera(self, n: int) -> None:
        self.current_camera = n
        self.power = max(0, self.power - 1)

    async def exit_camera(self) -> None:
        self.camera_on = False

    async def restart_game(self, interaction: discord.Interaction) -> None:
        assert self.game_message is not None
        await self.game_message.edit(embed=None, view=None)
        new_game = FNAFDiscordGame(self.channel, self.user, self.active_games)
        self.active_games[self.user.id] = new_game
        await new_game.start_game()

    async def quit_game(self, interaction: discord.Interaction) -> None:
        self.game_active = False
        assert self.game_message is not None
        await self.game_message.edit(
            embed=discord.Embed(title="👋 Thanks for playing!"),
            view=None,
        )
        _ = self.active_games.pop(self.user.id, None)

    async def start_game(
        self,
        existing_message: discord.Message | None = None,
    ) -> None:
        self.game_active = True
        embed, img = create_embed(self.get_game_state())
        self.view = FNAFGameView(self)
        file = discord.File(f"assets/{img}", filename=img)
        self.game_message = await self.channel.send(
            embed=embed, view=self.view, file=file
        )
        self.game_task = asyncio.create_task(self.game_loop())
