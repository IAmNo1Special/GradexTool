# Gradex Tool

A comprehensive Discord bot for the Revomon gaming community, providing game data lookup, competitive analysis tools, leaderboards, and real-time price tracking.

## Features

- **The Elder's Library**: Extensive search commands for Revomon game data

  - Ability, item, move, nature, and Revomon lookups
  - Evolution trees and spawn information
  - Type charts and tier lists

- **Grappraisal**: Competitive grading system for Revomon

  - IV/EV analysis with role-based stat weights
  - Grade letter and percentage calculations
  - Visual grade breakdowns

- **Leaderboards**: Real-time podium and PvP rankings

  - Current podium leaderboard
  - Weekly podium tracking
  - PvP rankings display

- **Price Tracking**: Live REVO token price updates

  - Updates Discord channel name every 3 minutes
  - Coingecko API integration

- **Land Integration**: Immutable X land NFT data

  - Land owner information
  - Sales data tracking (updated every 10 minutes)
  - Biome and rarity information

- **User Management**: Pro Tamer role verification

  - Automatic user tracking
  - Role-based access control
  - DM restrictions for non-Pro users

## Requirements

- Python 3.13+
- Discord Bot Token
- Discord Application ID

## Installation

1.Clone the repository:

```bash
git clone https://github.com/IAmNo1Special/GradexTool.git
cd GradexTool
```

2.Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3.Install dependencies:

```bash
pip install -r requirements.txt
# or using uv
uv sync
```

4.Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your Discord credentials:

```toml
DISCORD_BOT_TOKEN=your_bot_token_here
APPLICATION_ID=your_application_id_here
```

5.Configure guild settings in `configs/config.yaml`:

```yaml
gra_guild_id: 975120830193369088
pro_tamer_role_ids:
  - 1075670121097469965
  - 997404663525683263
  # Add your Pro Tamer role IDs
```

## Usage

### Running the Bot

Standard mode (with database rebase):

```bash
python main.py
```

The bot will:

1. Rebuild the Gradex database from JSON sources and APIs
1. Load all mods
1. Start the Discord bot
1. Sync slash commands

### Database Rebase

To rebuild the database without starting the bot, modify `main.py`:

```python
if __name__ == "__main__":
    import asyncio
    asyncio.run(entrypoint(rebase=False))  # Set to False to skip rebase
```

## Project Structure

```text
GradexTool/
├── configs/           # Configuration files
│   ├── config.yaml    # Guild and role settings
│   └── logging_config.py  # Logging setup
├── data/              # Database and JSON data files
│   ├── gradex.db      # SQLite database (93MB)
│   ├── gradexDB.py    # Database table classes
│   └── *.json         # Game data sources
├── mods/              # Discord bot extensions
│   ├── revomon/       # Leaderboards and price tracking
│   ├── the_elders_library/  # Game data lookups
│   ├── grappraisal/   # Competitive grading
│   ├── tiptops_shop/  # Shop functionality
│   └── guardrails/    # User management
├── utils/             # Utility functions
│   ├── revomon_utils.py    # Game logic and calculations
│   ├── embed_utils.py      # Discord embed builders
│   ├── button_utils.py     # Interactive button views
│   ├── land_utils.py       # Immutable X API integration
│   └── helpers.py          # User management helpers
├── main.py            # Bot entry point
├── pyproject.toml     # Project configuration
└── requirements.txt   # Python dependencies
```

## Database Tables

The SQLite database (`gradex.db`) contains 13 tables:

- `abilities` - Revomon abilities
- `capsules` - Move capsules
- `counterdex` - Competitive counter information
- `currentPodium` - Current leaderboard
- `fruitys` - Fruity items
- `items` - Game items
- `moves` - Revomon moves
- `natures` - Revomon natures
- `ownedLands` - Land NFT ownership
- `revomon` - Revomon base data
- `revomonMoves` - Revomon-move relationships
- `types` - Type effectiveness charts
- `users` - User tracking
- `weeklyPodium` - Weekly leaderboard

## Available Commands

### Slash Commands

- `/help` - Display help menu
- `/grade` - Grade a Revomon competitively
- `/podium` - Display current podium leaderboard
- `/pvp` - Display PvP leaderboard
- `/evchart` - Display EV chart
- `/evolutions` - Display evolution trees
- `/sapdaddy` - Display SapDaddy's library
- `/search [category] [keyword]` - Search game data

### Keyword Triggers

The bot responds to keywords in messages for quick lookups:

- Ability names (e.g., "adaptability")
- Item names
- Move names
- Nature names
- Revomon names
- Type combinations

## Development

### Code Style

The project uses Ruff for linting with the following configuration:

- Line length: 88 characters
- Target Python version: 3.13
- Google docstring convention

### Adding a New Mod

1. Create a new directory in `mods/` or add a file directly
1. Create a cog class inheriting from `commands.Cog`
1. Implement the `setup(gradex_bot)` async function
1. The mod loader will automatically discover and load it

Example:

```python
from discord.ext import commands

class MyMod(commands.Cog):
    def __init__(self, gradex: commands.Bot):
        self.gradex = gradex

    @commands.Cog.listener()
    async def on_ready(self):
        print("MyMod is ready!")

async def setup(gradex: commands.Bot):
    await gradex.add_cog(MyMod(gradex))
```

### Adding a Database Table

1. Create a new table class in `data/gradexDB.py`
1. Implement `create()`, `rebuild()`, `export_to_json()`, `count_entries()`
1. Add it to the `update_gradex_db()` function
1. Use the pattern from existing tables

## Known Issues

See `TODOS/TODO.md` for current issues and improvements needed:

- Database connection exhaustion in user checks
- Fragile data indexing with hardcoded indices
- Command syncing rate limiting on bot ready

## License

This project is part of the Global Revomon Association.

## Support

For issues or questions, contact the Global Revomon Association community.
