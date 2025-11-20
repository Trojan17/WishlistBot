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

# Configuration - Replace these with your actual values
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# The specific channel ID where commands are allowed
# This channel ID will work on whichever server contains it
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID", "0"))

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

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

    if ALLOWED_CHANNEL_ID:
        print(f"Commands restricted to channel ID: {ALLOWED_CHANNEL_ID}")
    else:
        print("Commands allowed in all channels")
    print("------")

    # Sync slash commands globally (works on all servers)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


def check_channel_allowed(interaction: discord.Interaction) -> bool:
    """Check if the command is allowed in this channel."""
    # If no channel restriction set, allow all channels
    if not ALLOWED_CHANNEL_ID:
        return True

    # Check if current channel matches the allowed channel
    return interaction.channel_id == ALLOWED_CHANNEL_ID


@bot.tree.command(
    name="add",
    description="Add a message to the list"
)
@app_commands.describe(message="The message you want to add")
async def add_command(interaction: discord.Interaction, message: str):
    """
    Slash command to add a message.
    Only works in the specified channel (if configured).
    """
    # Check if command is used in the allowed channel
    if not check_channel_allowed(interaction):
        await interaction.response.send_message(
            f"❌ This command can only be used in <#{ALLOWED_CHANNEL_ID}>",
            ephemeral=True  # Only visible to the user
        )
        return

    # Add the message to our storage
    entry = {
        "guild_id": interaction.guild_id,
        "guild_name": interaction.guild.name,
        "user": interaction.user.name,
        "user_id": interaction.user.id,
        "message": message,
        "timestamp": interaction.created_at.isoformat()
    }
    added_messages.append(entry)

    # Send confirmation
    await interaction.response.send_message(
        f"✅ Message added by {interaction.user.mention}:\n> {message}",
        ephemeral=False  # Visible to everyone
    )

    # Log to console with guild info
    print(f"[ADD] [{interaction.guild.name} ({interaction.guild_id})] {interaction.user.name}: {message}")


@bot.tree.command(
    name="list",
    description="List all added messages"
)
async def list_command(interaction: discord.Interaction):
    """
    Slash command to list all added messages for this server.
    Only works in the specified channel (if configured).
    """
    # Check if command is used in the allowed channel
    if not check_channel_allowed(interaction):
        await interaction.response.send_message(
            f"❌ This command can only be used in <#{ALLOWED_CHANNEL_ID}>",
            ephemeral=True
        )
        return

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
        ephemeral=False
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
    if not check_channel_allowed(interaction):
        await interaction.response.send_message(
            f"❌ This command can only be used in <#{ALLOWED_CHANNEL_ID}>",
            ephemeral=True
        )
        return

    # Count and remove only this guild's messages
    global added_messages
    guild_id = interaction.guild_id
    count = len([m for m in added_messages if m.get("guild_id") == guild_id])
    added_messages = [m for m in added_messages if m.get("guild_id") != guild_id]

    await interaction.response.send_message(
        f"🗑️ Cleared {count} message(s) from this server.",
        ephemeral=False
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
        f"• Channel ID: `{interaction.channel_id}`\n"
        f"• Your ID: `{interaction.user.id}`\n"
    )

    if ALLOWED_CHANNEL_ID:
        info_text += f"• Allowed Channel: <#{ALLOWED_CHANNEL_ID}>"
    else:
        info_text += "• Allowed Channel: All channels"

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
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ERROR: Please set your bot token in the .env file or environment variables!")
        print("See README.md for setup instructions.")
    else:
        bot.run(BOT_TOKEN)