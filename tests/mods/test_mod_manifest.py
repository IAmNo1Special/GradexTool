from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from mods import _read_enabled_mods, load_mods


def _make_mod_dir(base: Path, name: str, files: list[str]) -> None:
    mod_dir = base / name
    mod_dir.mkdir(parents=True, exist_ok=True)
    for filename in files:
        (mod_dir / filename).write_text("# fake cog\n")


def _loaded_names(bot: Any) -> set[str]:
    return {call.args[0] for call in bot.load_extension.call_args_list}


def _fake_mods_dir(tmp_path: Path) -> Path:
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    _make_mod_dir(mods_dir, "revomon", ["revo.py", "shared.py"])
    _make_mod_dir(mods_dir, "guardrails", ["users.py"])
    _make_mod_dir(mods_dir, "elevens_arena", ["tierlist1.py"])
    _make_mod_dir(mods_dir, "example_mod", ["base_cog.py"])
    return mods_dir


class TestModManifest:
    @pytest.mark.asyncio
    async def test_missing_manifest_keeps_current_behavior(self, tmp_path: Path) -> None:
        mods_dir = _fake_mods_dir(tmp_path)
        bot = MagicMock()
        bot.load_extension = AsyncMock()

        await load_mods(bot, mods_dir=mods_dir)

        loaded = _loaded_names(bot)
        assert "mods.revomon.revo" in loaded
        assert "mods.guardrails.users" in loaded
        # Previously skipped mods stay off.
        assert not any(name.startswith("mods.elevens_arena") for name in loaded)
        assert not any(name.startswith("mods.example_mod") for name in loaded)
        # Helper cog modules stay off even without a manifest.
        assert "mods.revomon.shared" not in loaded

    @pytest.mark.asyncio
    async def test_manifest_can_disable_a_mod(self, tmp_path: Path) -> None:
        mods_dir = _fake_mods_dir(tmp_path)
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("enabled:\n  - revomon\n")
        bot = MagicMock()
        bot.load_extension = AsyncMock()

        await load_mods(bot, mods_dir=mods_dir, manifest_path=manifest)

        loaded = _loaded_names(bot)
        assert "mods.revomon.revo" in loaded
        assert not any(name.startswith("mods.guardrails") for name in loaded)

    @pytest.mark.asyncio
    async def test_manifest_can_enable_a_previously_skipped_mod(self, tmp_path: Path) -> None:
        mods_dir = _fake_mods_dir(tmp_path)
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("enabled:\n  - revomon\n  - elevens_arena\n")
        bot = MagicMock()
        bot.load_extension = AsyncMock()

        await load_mods(bot, mods_dir=mods_dir, manifest_path=manifest)

        loaded = _loaded_names(bot)
        assert "mods.elevens_arena.tierlist1" in loaded
        # example_mod was not listed, so it stays off.
        assert not any(name.startswith("mods.example_mod") for name in loaded)

    @pytest.mark.asyncio
    async def test_manifest_cannot_enable_helper_cog_modules(self, tmp_path: Path) -> None:
        mods_dir = _fake_mods_dir(tmp_path)
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("enabled:\n  - revomon\n  - shared\n")
        bot = MagicMock()
        bot.load_extension = AsyncMock()

        await load_mods(bot, mods_dir=mods_dir, manifest_path=manifest)

        assert "mods.revomon.shared" not in _loaded_names(bot)

    def test_malformed_manifest_falls_back_to_defaults(self, tmp_path: Path) -> None:
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("enabled: not-a-list\n")
        assert _read_enabled_mods(tmp_path, manifest) is None

    def test_missing_manifest_reads_as_none(self, tmp_path: Path) -> None:
        assert _read_enabled_mods(tmp_path, tmp_path / "nope.yaml") is None

    def test_shipped_manifest_matches_current_behavior(self) -> None:
        repo_mods = Path(__file__).resolve().parents[2] / "mods"
        enabled = _read_enabled_mods(repo_mods)
        assert enabled is not None
        assert "elevens_arena" not in enabled
        assert "example_mod" not in enabled
        assert {"core", "revomon", "guardrails", "revocord"}.issubset(enabled)
