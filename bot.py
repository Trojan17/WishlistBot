"""
Discord Bot with /add command
This bot provides a /add slash command that only works in a specific channel.
"""

import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# The channel where the bot will POST messages
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

# Set up intents
intents = discord.Intents.default()
# Note: message_content intent not needed for slash commands only
# Enable it in Discord Developer Portal if you add message-based features

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Store for added messages (in production, use a database)
added_messages = []


@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

    # List all guilds the bot is in
    print(f"Connected to {len(bot.guilds)} server(s):")
    for guild in bot.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")
    print("------")

    if TARGET_CHANNEL_ID:
        print(f"Messages will be posted to channel ID: {TARGET_CHANNEL_ID}")
    else:
        print("WARNING: TARGET_CHANNEL_ID not set!")
    print("------")

    # Sync slash commands globally (works on all servers)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.tree.command(
    name="add",
    description="Add a message to the watchlist channel"
)
@app_commands.describe(message="The message you want to add")
async def add_command(interaction: discord.Interaction, message: str):
    """
    Slash command to add a message.
    Can be used in any channel, posts to the target channel.
    """
    # Get the target channel
    target_channel = bot.get_channel(TARGET_CHANNEL_ID)

    if not target_channel:
        await interaction.response.send_message(
            "❌ Target channel not found. Please check the bot configuration.",
            ephemeral=True
        )
        return

    # Check if bot has permission to send in target channel
    if not target_channel.permissions_for(interaction.guild.me).send_messages:
        await interaction.response.send_message(
            f"❌ I don't have permission to send messages in {target_channel.mention}",
            ephemeral=True
        )
        return

    # Post the message to the target channel
    posted_message = await target_channel.send(
        f"**Added by {interaction.user.mention}:**\n> {message}"
    )

    # Store the message info
    entry = {
        "guild_id": interaction.guild_id,
        "guild_name": interaction.guild.name,
        "user": interaction.user.name,
        "user_id": interaction.user.id,
        "message": message,
        "message_id": posted_message.id,
        "timestamp": interaction.created_at.isoformat()
    }
    added_messages.append(entry)

    # Send confirmation to the user (ephemeral = only they see it)
    await interaction.response.send_message(
        f"✅ Message posted to {target_channel.mention}",
        ephemeral=True
    )

    # Log to console
    print(f"[ADD] [{interaction.guild.name}] {interaction.user.name}: {message}")


@bot.tree.command(
    name="list",
    description="List all added messages"
)
async def list_command(interaction: discord.Interaction):
    """
    Slash command to list all added messages for this server.
    """
    # Filter messages for this guild only
    guild_messages = [m for m in added_messages if m.get("guild_id") == interaction.guild_id]

    if not guild_messages:
        await interaction.response.send_message(
            "📭 No messages have been added yet in this server.",
            ephemeral=True
        )
        return

    # Format the messages
    messages_text = "\n".join([
        f"• **{entry['user']}**: {entry['message']}"
        for entry in guild_messages[-10:]  # Show last 10
    ])

    await interaction.response.send_message(
        f"📋 **Added Messages** (showing last {min(10, len(guild_messages))}):\n{messages_text}",
        ephemeral=True
    )


@bot.tree.command(
    name="clear",
    description="Clear all added messages (Admin only)"
)
@app_commands.checks.has_permissions(administrator=True)
async def clear_command(interaction: discord.Interaction):
    """
    Slash command to clear all messages for this server.
    Only available to administrators.
    """
    # Count and remove only this guild's messages
    global added_messages
    guild_id = interaction.guild_id
    count = len([m for m in added_messages if m.get("guild_id") == guild_id])
    added_messages = [m for m in added_messages if m.get("guild_id") != guild_id]

    await interaction.response.send_message(
        f"🗑️ Cleared {count} message(s) from this server.",
        ephemeral=True
    )


@bot.tree.command(
    name="info",
    description="Show bot info and server details"
)
async def info_command(interaction: discord.Interaction):
    """Show information about the current server."""
    guild = interaction.guild

    info_text = (
        f"**Server Info**\n"
        f"• Name: {guild.name}\n"
        f"• Server ID: `{guild.id}`\n"
        f"• This Channel ID: `{interaction.channel_id}`\n"
        f"• Your ID: `{interaction.user.id}`\n"
    )

    if TARGET_CHANNEL_ID:
        info_text += f"• Target Channel: <#{TARGET_CHANNEL_ID}>"
    else:
        info_text += "• Target Channel: Not configured"

    await interaction.response.send_message(info_text, ephemeral=True)


@clear_command.error
async def clear_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle errors for the clear command."""
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.",
            ephemeral=True
        )


# Run the bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN environment variable is not set!")
    bot.run(BOT_TOKEN)