<div align="center">

# 🎮 Gradex Tool

**A comprehensive Discord bot for the Revomon gaming community**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Discord](https://img.shields.io/badge/discord.py-2.7+-green.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-Global%20Revomon%20Association-purple.svg)](https://github.com/IAmNo1Special/GradexTool)

Providing game data lookup, competitive analysis tools, leaderboards, and real-time price tracking.

</div>

______________________________________________________________________

## ✨ Features

### 📚 The Elder's Library

Extensive search commands for Revomon game data

- **Ability, item, move, nature, and Revomon lookups** - Instant data retrieval
- **Evolution trees and spawn information** - Complete evolution chains
- **Type charts and tier lists** - Competitive analysis tools
- **Keyword triggers** - Quick lookups by typing ability/item/move names

### 🏆 Grappraisal

Competitive grading system for Revomon

- **IV/EV analysis with role-based stat weights** - Smart stat evaluation
- **Grade letter and percentage calculations** - A+ to F- grading scale
- **Visual grade breakdowns** - Interactive charts with Plotly
- **Nature quality assessment** - Perfect/Good/Neutral/Poor ratings
- **Save & Flex features** - Share your graded Revomon

### 🏅 Leaderboards

Real-time podium and PvP rankings

- **Current podium leaderboard** - Live top 3 players
- **Weekly podium tracking** - Weekly competition results
- **PvP rankings display** - Elo, wins, losses, win rates
- **Auto-generated podium images** - Visual leaderboard displays

### 🎯 RevoCord RPG System

In-game Discord integration

- **Wild spawn system** - Biome-based Revomon encounters
- **Travel system** - Move between cities with energy management
- **Account tracking** - Trainer level, XP, coins, inventory
- **Encounter broadcasting** - Real-time spawn notifications
- **Activity dashboard** - User statistics and progress

### 🛡️ Core Bot Features

Essential bot infrastructure

- **Channel enforcement** - Automatic channel layout protection
- **Health monitoring** - Periodic heartbeat logging (5-minute intervals)
- **User management** - Pro Tamer role verification
- **DM restrictions** - Access control for non-Pro users

### 🌐 External Integrations

- **Revomon API** - Game data and leaderboards
- **PokeAPI** - Abilities, natures, items data
- **Immutable X** - Land NFT ownership and sales data

## 📋 Requirements

- **Python 3.12+** (3.13+ recommended)
- **Discord Bot Token**
- **Discord Application ID**

______________________________________________________________________

## 🚀 Installation

### ⚡ Quick Start with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/IAmNo1Special/GradexTool.git
cd GradexTool

# Install uv (if not already installed)
# On Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# On Unix: curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync

# Run the bot
uv run python main.py
```

### 🐍 Traditional Installation

```bash
# Clone the repository
git clone https://github.com/IAmNo1Special/GradexTool.git
cd GradexTool

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### ⚙️ Configuration

1. **Configure environment variables**:

```bash
cp .env.example .env
```

Edit `.env` and add your Discord credentials:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
APPLICATION_ID=your_application_id_here
```

2. **Configure guild settings** in configs/configs.yaml:

```yaml
GRA_GUILD_ID: 975120830193369088
PRO_TAMER_ROLE_IDS:
  - 1075670121097469965
  - 997404663525683263
  - 975592186177531914
  - 975592348744556555
  - 990783815771385896
```

______________________________________________________________________

## 💻 Usage

### Running the Bot

**With uv (recommended)**:

```bash
uv run python main.py
```

**With traditional venv**:

```bash
python main.py
```

The bot will:

1. Rebuild the Gradex database from JSON sources and APIs
1. Load all mods dynamically
1. Start the Discord bot
1. Sync slash commands

### Skipping Database Rebase

To start the bot without rebuilding the database, modify `main.py`:

```python
if __name__ == "__main__":
    import asyncio
    asyncio.run(entrypoint(rebase=False))  # Set to False to skip rebase
```

### Building Data Separately

To rebuild data without starting the bot:

```bash
# With uv
uv run python scripts/main.py

# With traditional venv
python scripts/main.py
```

______________________________________________________________________

## 📁 Project Structure

```text
GradexTool/
├── configs/              # Configuration files
│   ├── configs.yaml      # Guild, role, and API settings
│   └── logging_config.py # Centralized logging setup
├── data/                 # Database and JSON data files
│   ├── gradex.db         # SQLite database
│   ├── accounts.json     # RevoCord RPG accounts
│   └── *.json            # Game data sources
├── mods/                 # Discord bot extensions
│   ├── core/             # Core bot features
│   │   ├── enforcement.py    # Channel layout enforcement
│   │   └── health.py          # Health monitoring
│   ├── grappraisal/      # Competitive grading
│   │   ├── grade_command.py  # /grade slash command
│   │   └── grade_keyword.py  # Keyword triggers
│   ├── revocord/         # RevoCord RPG system
│   │   ├── hunting.py        # Wild spawn system
│   │   ├── shared.py         # Account management
│   │   ├── broadcaster.py    # Encounter broadcasting
│   │   ├── setup.py          # Guild setup
│   │   ├── portal.py         # Travel system
│   │   └── dashboard.py      # User dashboard
│   ├── revomon/          # Leaderboards
│   │   ├── podium_command.py # Podium display
│   │   ├── pvp_command.py    # PvP rankings
│   │   └── revo.py           # Revomon mod loader
│   ├── the_elders_library/ # Game data lookups
│   │   ├── search_command.py # Unified search
│   │   ├── abilities_keyword.py
│   │   ├── items_keyword.py
│   │   ├── moves_keyword.py
│   │   ├── natures_keyword.py
│   │   └── revomon_keyword.py
│   └── guardrails/       # User management
├── scripts/              # Data fetching scripts
│   ├── gradexDB.py       # Database table classes
│   ├── revomon.py        # Revomon data fetching
│   ├── abilities.py      # Abilities from PokeAPI
│   ├── moves.py          # Move data
│   ├── natures.py        # Nature data
│   ├── items.py          # Item data
│   ├── type_charts.py    # Type effectiveness
│   └── main.py           # Data build orchestrator
├── utils/                # Utility functions
│   ├── revomon_utils.py  # Game logic & grading
│   ├── helpers.py        # User management helpers
│   ├── embed_utils.py    # Discord embed builders
│   ├── button_utils.py   # Interactive button views
│   ├── land_utils.py     # Immutable X integration
│   └── emoji_utils.py    # Emoji utilities
├── tests/                # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── scripts/          # Script tests
│   └── mods/             # Mod tests
├── main.py               # Bot entry point
├── pyproject.toml        # Project configuration (uv)
└── requirements.txt      # Python dependencies
```

______________________________________________________________________

## 🗄️ Database Tables

The SQLite database (`data/gradex.db`) contains 14+ tables:

| Table | Description |
|-------|-------------|
| `abilities` | Revomon abilities from PokeAPI |
| `capsules` | Move capsules |
| `counterdex` | Competitive counter information and meta builds |
| current_podium | Current leaderboard data |
| weekly_podium | Weekly podium tracking |
| fruitys | Fruity items |
| items | Game items and medicines |
| moves | Revomon moves with priority |
| natures | Revomon natures with stat modifiers |
| ownedLands | Immutable X land NFT ownership |
| revomon | Revomon base data (stats, types, abilities) |
| revomon_moves | Revomon-move relationships |
| types | Type effectiveness charts |
| users | User tracking and Pro Tamer status |
| event_board_logs | Event board logging |
| active_spawns | Active wild spawn tracking |

______________________________________________________________________

## 🎮 Available Commands

### Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Display help menu |
| `/grade <catch_id>` | Grade a Revomon competitively |
| `/podium` | Display current & weekly podium leaderboards |
| `/pvp` | Display PvP leaderboard |
| `/evchart` | Display EV chart |
| `/evolutions` | Display evolution trees |
| `/sapdaddy` | Display SapDaddy's library |
| `/search [category] [keyword]` | Unified game data search |

### Keyword Triggers

The bot responds to keywords in messages for quick lookups:

- **Ability names** (e.g., "adaptability", "overgrow")
- **Item names** (e.g., "potion", "revive")
- **Move names** (e.g., "tackle", "flamethrower")
- **Nature names** (e.g., "adamant", "modest")
- **Revomon names** (e.g., "vyphern", "wyverdant")
- **Type combinations** (e.g., "fire dragonic")
- **"grade" / "appraise"** - Opens grading modal

______________________________________________________________________

## 🛠️ Development

### Code Style

The project uses **Ruff** for linting and formatting:

- **Line length**: 88 characters
- **Target Python**: 3.13
- **Docstring convention**: Google
- **Max complexity**: 55

**Linting with uv**:

```bash
# Check code
uv run ruff check .

# Format code
uv run ruff format .
```

**Linting with traditional venv**:

```bash
# Check code
ruff check .

# Format code
ruff format .
```

### Running Tests

**With uv (recommended)**:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=.

# Run specific test file
uv run pytest tests/scripts/test_revomon.py
```

**With traditional venv**:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

### Adding a New Mod

1. Create a new directory in `mods/` or add a file directly
1. Create a cog class inheriting from `commands.Cog`
1. Implement the `async def setup(gradex_bot)` function
1. The mod loader will automatically discover and load it

**Example**:

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

**Note**: The mod loader skips:

- Directories: `example_mod`, `elevens_arena`
- Files: `base_cog.py`, `shared.py`, `broadcaster.py`, `tv.py`

### Adding a Database Table

1. Create a new table class in `scripts/gradexDB.py`
1. Implement required methods:
   - `create()` - Drops and recreates table
   - `rebuild()` - Fetches data and inserts
   - `export_to_json()` - Exports to JSON
   - `count_entries()` - Returns row count
1. Add it to the `update_gradex_db()` function
1. Follow the pattern from existing tables

**Example pattern**:

```python
class MyTable:
    def __init__(self) -> None:
        self.db_path = db_path

    def _connect(self) -> Connection:
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        # Create table schema
        pass

    async def rebuild(self) -> None:
        # Fetch and insert data
        pass

    async def export_to_json(self) -> None:
        # Export to JSON
        pass

    async def count_entries(self) -> int:
        # Return count
        pass
```

______________________________________________________________________

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_BOT_TOKEN` | Discord bot token | ✅ Yes |
| `APPLICATION_ID` | Discord application ID | ✅ Yes |

### Config File (`configs/config.yaml`)

| Setting | Description |
|---------|-------------|
| `GRA_GUILD_ID` | Main Discord guild ID |
| `PRO_TAMER_ROLE_IDS` | List of Pro Tamer role IDs |
| `REVOMON_REVODEX_ENDPOINT` | Revomon API endpoint |
| `POKEAPI_NATURES_ENDPOINT` | PokeAPI natures endpoint |
| `GRADEX_DB_PATH` | Path to SQLite database |
| File paths | Paths to JSON data files and asset directories |

______________________________________________________________________

## 🐛 Known Issues

- **Database connection exhaustion** in user checks
- **Fragile data indexing** with hardcoded indices
- **Command syncing rate limiting** on bot ready

______________________________________________________________________

## 📝 License

This project is part of the **Global Revomon Association**.

______________________________________________________________________

## 🤝 Support

For issues or questions, contact the Global Revomon Association community.

______________________________________________________________________

<div align="center">

**Built with ❤️ for the Revomon Community**

[![uv](https://img.shields.io/badge/uv-0.5+-blue.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/ruff-0.15+-green.svg)](https://github.com/astral-sh/ruff)
[![Pytest](https://img.shields.io/badge/pytest-8.0+-yellow.svg)](https://pytest.org/)

</div>
