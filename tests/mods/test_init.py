from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mods import load_mods


class TestModsLoader:
    @pytest.mark.asyncio
    @patch('mods.Path')
    async def test_load_mods_success(self, mock_path_class):
        mock_bot = MagicMock()
        mock_bot.load_extension = AsyncMock()

        mock_mods_dir = MagicMock()
        mock_path_class.return_value.parent = mock_mods_dir

        # File in mods/
        mock_file1 = MagicMock()
        mock_file1.is_file.return_value = True
        mock_file1.suffix = '.py'
        mock_file1.name = 'test_mod.py'
        mock_file1.stem = 'test_mod'

        # Subdir in mods/
        mock_subdir = MagicMock()
        mock_subdir.is_dir.return_value = True
        mock_subdir.is_file.return_value = False
        mock_subdir.name = 'test_pkg'

        # File in subdir
        mock_file2 = MagicMock()
        mock_file2.suffix = '.py'
        mock_file2.name = 'test_cog.py'
        mock_file2.stem = 'test_cog'
        mock_subdir.iterdir.return_value = [mock_file2]

        mock_mods_dir.iterdir.return_value = [mock_file1, mock_subdir]

        await load_mods(mock_bot)

        assert mock_bot.load_extension.call_count == 2
        mock_bot.load_extension.assert_any_call('mods.test_mod')
        mock_bot.load_extension.assert_any_call('mods.test_pkg.test_cog')

    @pytest.mark.asyncio
    @patch('mods.Path')
    async def test_load_mods_exception(self, mock_path_class):
        mock_bot = MagicMock()
        mock_bot.load_extension = AsyncMock(side_effect=Exception("Load error"))

        mock_mods_dir = MagicMock()
        mock_path_class.return_value.parent = mock_mods_dir

        mock_file1 = MagicMock()
        mock_file1.is_file.return_value = True
        mock_file1.suffix = '.py'
        mock_file1.name = 'test_mod.py'
        mock_file1.stem = 'test_mod'

        mock_subdir = MagicMock()
        mock_subdir.is_dir.return_value = True
        mock_subdir.is_file.return_value = False
        mock_subdir.name = 'test_pkg'

        mock_file2 = MagicMock()
        mock_file2.suffix = '.py'
        mock_file2.name = 'test_cog.py'
        mock_file2.stem = 'test_cog'
        mock_subdir.iterdir.return_value = [mock_file2]

        mock_mods_dir.iterdir.return_value = [mock_file1, mock_subdir]

        await load_mods(mock_bot)

        assert mock_bot.load_extension.call_count == 2
