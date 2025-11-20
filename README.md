# Discord Bot with /add Command

A simple Discord bot that provides a `/add` slash command restricted to a specific channel on your server.

## Features

- `/add <message>` - Add a message (only works in the designated channel)
- `/list` - View all added messages
- `/clear` - Clear all messages (admin only)
- Channel restriction for commands
- Uses modern Discord.py 2.0+ slash commands

## Setup Instructions

### 1. Create a Discord Bot Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent (if needed for future features)
6. Copy the bot token (click "Reset Token" if needed) - **keep this secret!**

### 2. Invite the Bot to Your Server

1. In the Developer Portal, go to "OAuth2" > "URL Generator"
2. Select these scopes:
   - `bot`
   - `applications.commands`
3. Select these bot permissions:
   - Send Messages
   - Use Slash Commands
   - Read Message History (optional)
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Get Your Server and Channel IDs

1. Enable Developer Mode in Discord:
   - User Settings > App Settings > Advanced > Developer Mode
2. Right-click your server name > "Copy Server ID" → This is your `GUILD_ID`
3. Right-click the channel where you want `/add` to work > "Copy Channel ID" → This is your `ALLOWED_CHANNEL_ID`

### 4. Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token
   GUILD_ID=123456789012345678
   ALLOWED_CHANNEL_ID=123456789012345678
   ```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Bot

```bash
python bot.py
```

The bot will sync the slash commands to your server. This may take a few seconds.

## Hosting Options

### Free Hosting Services

1. **Bot-Hosting.net** (https://bot-hosting.net)
   - Free 24/7 hosting
   - Supports Python, Node.js, Java
   - Uses a coin system for resources

2. **Wispbyte** (https://wispbyte.com)
   - Free 24/7 hosting
   - Supports Python and JavaScript
   - No hidden fees

3. **Oracle Cloud Free Tier** (https://cloud.oracle.com)
   - Up to 24GB RAM and 4 vCPUs free
   - ARM-based instances
   - Great for larger bots

4. **Railway** (https://railway.app)
   - $5 free credit monthly
   - Easy deployment from GitHub

5. **Fly.io** (https://fly.io)
   - Free tier available
   - Easy Docker deployment

### Self-Hosting (VPS)

If using a VPS (like Oracle Cloud, DigitalOcean, Vultr, etc.):

1. **Using systemd** (recommended for Linux):

   Create `/etc/systemd/system/discord-bot.service`:
   ```ini
   [Unit]
   Description=Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/path/to/discord_bot
   ExecStart=/usr/bin/python3 bot.py
   Restart=always
   RestartSec=10
   EnvironmentFile=/path/to/discord_bot/.env

   [Install]
   WantedBy=multi-user.target
   ```

   Then run:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   ```

2. **Using screen or tmux**:
   ```bash
   screen -S discord-bot
   python bot.py
   # Press Ctrl+A, D to detach
   ```

3. **Using Docker**:

   Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["python", "bot.py"]
   ```

   Build and run:
   ```bash
   docker build -t discord-bot .
   docker run -d --env-file .env --name discord-bot discord-bot
   ```

## Usage

Once the bot is running and added to your server:

1. Go to the channel you specified as `ALLOWED_CHANNEL_ID`
2. Type `/add ` and Discord will show the command
3. Enter your message and press Enter

The command will only work in the specified channel. Using it elsewhere will show an error message only visible to you.

## Customization

### Adding More Commands

To add more slash commands, follow this pattern in `bot.py`:

```python
@bot.tree.command(
    name="your_command",
    description="Description of your command",
    guild=discord.Object(id=GUILD_ID)
)
async def your_command(interaction: discord.Interaction):
    await interaction.response.send_message("Your response")
```

### Using a Database

For production, replace the `added_messages` list with a database. Popular options:
- SQLite (built into Python)
- PostgreSQL
- MongoDB

### Global Commands

To make commands work in all servers (takes up to 1 hour to register):

1. Remove `guild=discord.Object(id=GUILD_ID)` from command decorators
2. Change the sync in `on_ready`:
   ```python
   synced = await bot.tree.sync()
   ```

## Troubleshooting

### Commands not appearing

- Wait a few minutes after starting the bot
- Make sure the bot has `applications.commands` scope
- Check that `GUILD_ID` is correct
- Try kicking and re-inviting the bot

### "Unknown interaction" error

- The bot may have disconnected; restart it
- Check your internet connection

### Permission errors

- Ensure the bot has "Use Slash Commands" permission
- Check channel-specific permission overwrites

## License

MIT License - feel free to modify and use as you wish!