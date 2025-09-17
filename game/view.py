import discord
import asyncio

class FNAFGameView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()

        if self.game.game_over or self.game.won:
            restart_button = discord.ui.Button(label="🔄 Restart", style=discord.ButtonStyle.green)
            restart_button.callback = self.restart_callback
            self.add_item(restart_button)

            quit_button = discord.ui.Button(label="❌ Quit", style=discord.ButtonStyle.red)
            quit_button.callback = self.quit_callback
            self.add_item(quit_button)
            return

        if self.game.camera_on:
            for i in range(1, 7):
                button = discord.ui.Button(
                    label=f"Cam {i}",
                    style=discord.ButtonStyle.primary if self.game.current_camera == i else discord.ButtonStyle.secondary,
                    custom_id=f"cam_{i}",
                    row=0 if i <= 3 else 1
                )
                button.callback = self.camera_callback
                self.add_item(button)

            exit_button = discord.ui.Button(label="📱 Exit Cameras", style=discord.ButtonStyle.danger)
            exit_button.callback = self.exit_camera_callback
            self.add_item(exit_button)
            return

        light_button = discord.ui.Button(
            label="💡 Light",
            style=discord.ButtonStyle.success if self.game.light_on else discord.ButtonStyle.secondary
        )
        light_button.callback = self.light_callback
        self.add_item(light_button)

        door_button = discord.ui.Button(
            label="🚪 Door",
            style=discord.ButtonStyle.danger if self.game.door_closed else discord.ButtonStyle.secondary
        )
        door_button.callback = self.door_callback
        self.add_item(door_button)

        camera_button = discord.ui.Button(label="📹 Cameras", style=discord.ButtonStyle.primary)
        camera_button.callback = self.camera_open_callback
        self.add_item(camera_button)

        quit_button = discord.ui.Button(label="❌ Quit", style=discord.ButtonStyle.red)
        quit_button.callback = self.quit_callback
        self.add_item(quit_button)

    async def light_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        if self.game.power > 0 and not self.game.door_closed:
            self.game.light_on = not self.game.light_on
        asyncio.create_task(self.game.update_game_display(force=True))

    async def door_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        if self.game.power <= 0: return
        self.game.door_closed = not self.game.door_closed
        asyncio.create_task(self.game.update_game_display(force=True))

    async def camera_open_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        if self.game.power <= 0: return
        await self.game.open_camera()
        asyncio.create_task(self.game.update_game_display(force=True))

    async def camera_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        cam_num = int(interaction.data["custom_id"].split("_")[1])
        await self.game.switch_camera(cam_num)
        asyncio.create_task(self.game.update_game_display(force=True))

    async def exit_camera_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        await self.game.exit_camera()
        asyncio.create_task(self.game.update_game_display(force=True))

    async def restart_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        await self.game.restart_game(interaction)

    async def quit_callback(self, interaction):
        if interaction.user.id != self.game.user.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        await interaction.response.defer(thinking=False)
        await self.game.quit_game(interaction)