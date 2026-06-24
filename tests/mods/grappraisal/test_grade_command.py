from io import BytesIO
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from mods.grappraisal.grade_command import GradeCommand, setup


@pytest.fixture
def grade_cog(mock_bot: Any) -> Any:
    return GradeCommand(mock_bot)


@pytest.fixture
def mock_mon_info(sample_revomon_data: Any, sample_grade_data: Any) -> Any:
    data = sample_revomon_data.copy()
    data.update(sample_grade_data)
    data["image_bytes"] = BytesIO(b"dummy")
    return data


@pytest.mark.asyncio
async def test_setup(mock_bot: Any) -> None:
    await setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
    assert isinstance(mock_bot.add_cog.call_args[0][0], GradeCommand)


def test_initialization(grade_cog: Any, mock_bot: Any) -> None:
    assert grade_cog.gradex == mock_bot
    assert hasattr(grade_cog, "mon_manager")


@pytest.mark.asyncio
async def test_on_ready(grade_cog: Any) -> None:
    grade_cog.gradex.add_view = MagicMock()
    await grade_cog.on_ready()
    assert grade_cog.gradex.add_view.call_count == 3


def test_mon_info_embed1(grade_cog: Any, mock_mon_info: Any) -> None:
    user_id = 123
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info
    embed = grade_cog.mon_info_embed1(user_id)
    assert isinstance(embed, discord.Embed)
    assert "Testmon" in embed.title  # type: ignore[operator]


@patch("mods.grappraisal.grade_command.create_graded_mon_img")
def test_graded_mon_embed(mock_create_img: Any, grade_cog: Any, mock_mon_info: Any) -> None:
    user_id = 123
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info

    mock_img = MagicMock()
    mock_create_img.return_value = mock_img

    embed = grade_cog.graded_mon_embed(user_id)
    assert isinstance(embed, discord.Embed)
    assert "Grade:" in embed.title  # type: ignore[operator]
    mock_img.save.assert_called_once()


def test_grade_breakdown_embed(grade_cog: Any, mock_mon_info: Any) -> None:
    user_id = 123
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info

    embed = grade_cog.grade_breakdown_embed(user_id)
    assert isinstance(embed, discord.Embed)
    assert "Breakdown:" in embed.title  # type: ignore[operator]

    # Test alternative branches
    mock_mon_info["stat_weights"]["def"] = 0.1
    mock_mon_info["role"] = "Special Attacker"
    mock_mon_info["atk_iv"] = 4
    mock_mon_info["nature_quality"] = "Good"
    embed2 = grade_cog.grade_breakdown_embed(user_id)
    assert "Perfect 0-IV" in embed2.fields[0].value

    mock_mon_info["stat_weights"]["spa"] = 0.5
    mock_mon_info["role"] = "Special Attacker"
    mock_mon_info["atk_iv"] = 31
    mock_mon_info["nature_quality"] = "Poor"
    embed3 = grade_cog.grade_breakdown_embed(user_id)
    assert "Penalized" in embed3.fields[0].value

    mock_mon_info["nature_quality"] = "Neutral"
    embed4 = grade_cog.grade_breakdown_embed(user_id)
    assert isinstance(embed4, discord.Embed)

@pytest.mark.asyncio
@patch("mods.grappraisal.grade_command.appraise_revomon")
@patch("mods.grappraisal.grade_command.GradeCommand.graded_mon_embed")
async def test_mon_info_buttons1_grade_button(mock_embed: Any, mock_appraise: Any, mock_interaction: Any, mock_mon_info: Any) -> None:
    user_id = mock_interaction.user.id
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info
    mock_appraise.return_value = {"grade_percent": 99}

    view = GradeCommand.MonInfoButtons1()
    button = view.children[0]

    await button.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.edit_message.assert_called()
    assert GradeCommand.mon_manager.mon_info[user_id]["grade_percent"] == 99

@pytest.mark.asyncio
async def test_mon_info_buttons1_grade_button_exception(mock_interaction: Any) -> None:
    # Exception handling
    view = GradeCommand.MonInfoButtons1()
    button = view.children[0]
    mock_interaction.user.id = 999  # No data in mon_info
    await button.callback(mock_interaction)

@pytest.mark.asyncio
async def test_exit_message_button(mock_interaction: Any) -> None:
    view = GradeCommand.ExitMessageButton()
    button = view.children[0]
    await button.callback(mock_interaction)
    mock_interaction.message.delete.assert_called_once()

@pytest.mark.asyncio
@patch("mods.grappraisal.grade_command.GradeCommand.graded_mon_embed")
async def test_mon_info_buttons6_save(mock_embed: Any, mock_interaction: Any, mock_mon_info: Any) -> None:
    user_id = mock_interaction.user.id
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info

    view = GradeCommand.MonInfoButtons6()
    save_btn = view.children[0]

    # In guild
    mock_interaction.guild = MagicMock()
    mock_interaction.user.send = AsyncMock()
    await save_btn.callback(mock_interaction)
    mock_interaction.user.send.assert_called_once()

    # Not in guild
    mock_interaction.guild = None
    mock_interaction.user.send = AsyncMock()
    await save_btn.callback(mock_interaction)
    # the second send happens via followup.send in else block

@pytest.mark.asyncio
async def test_mon_info_buttons6_save_exception(mock_interaction: Any) -> None:
    view = GradeCommand.MonInfoButtons6()
    save_btn = view.children[0]
    mock_interaction.user.id = 999
    await save_btn.callback(mock_interaction)


@pytest.mark.asyncio
@patch("mods.grappraisal.grade_command.GradeCommand.graded_mon_embed")
async def test_mon_info_buttons6_flex(mock_embed: Any, mock_interaction: Any, mock_mon_info: Any) -> None:
    user_id = mock_interaction.user.id
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info
    view = GradeCommand.MonInfoButtons6()
    flex_btn = view.children[1]

    await flex_btn.callback(mock_interaction)
    mock_interaction.followup.send.assert_called()

@pytest.mark.asyncio
async def test_mon_info_buttons6_flex_exception(mock_interaction: Any) -> None:
    view = GradeCommand.MonInfoButtons6()
    flex_btn = view.children[1]
    mock_interaction.user.id = 999
    await flex_btn.callback(mock_interaction)

@pytest.mark.asyncio
@patch("mods.grappraisal.grade_command.GradeCommand.grade_breakdown_embed")
async def test_mon_info_buttons6_why(mock_embed: Any, mock_interaction: Any, mock_mon_info: Any) -> None:
    user_id = mock_interaction.user.id
    GradeCommand.mon_manager.mon_info[user_id] = mock_mon_info
    view = GradeCommand.MonInfoButtons6()
    why_btn = view.children[2]

    await why_btn.callback(mock_interaction)
    mock_interaction.response.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_mon_info_buttons6_why_exception(mock_interaction: Any) -> None:
    view = GradeCommand.MonInfoButtons6()
    why_btn = view.children[2]
    mock_interaction.user.id = 999
    await why_btn.callback(mock_interaction)

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
@patch("mods.grappraisal.grade_command.create_graded_mon_img")
@patch("mods.grappraisal.grade_command.GradeCommand.mon_info_embed1")
async def test_grade_command_success(mock_embed: Any, mock_create_img: Any, mock_get: Any, grade_cog: Any, mock_interaction: Any) -> None:
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "data": {
            "catchedRevomon": {
                "name": "Testmon",
                "nature": "Adamant",
                "ability": "Overgrow",
                "shiny": False,
                "ivhp": "31", "ivatk": "31", "ivdef": "31",
                "ivspa": "31", "ivspd": "31", "ivspe": "31"
            }
        }
    }
    # Setup context manager for mock_get
    mock_get.return_value.__aenter__.return_value = mock_response

    mock_img = MagicMock()
    mock_create_img.return_value = mock_img

    await grade_cog.grade.callback(grade_cog, mock_interaction, catch_id=1234)

    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    assert GradeCommand.mon_manager.mon_info[mock_interaction.user.id]["catch_id"] == 1234

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_grade_command_invalid_id(mock_get: Any, grade_cog: Any, mock_interaction: Any) -> None:
    mock_response = AsyncMock()
    mock_response.json.return_value = {"data": None}
    mock_get.return_value.__aenter__.return_value = mock_response

    await grade_cog.grade.callback(grade_cog, mock_interaction, catch_id=9999)

    mock_interaction.followup.send.assert_called_with("Invalid Revomon ID. Please try again.", ephemeral=True)

@pytest.mark.asyncio
async def test_grade_command_exception(grade_cog: Any, mock_interaction: Any) -> None:
    mock_interaction.response.defer.side_effect = Exception("Boom")
    await grade_cog.grade.callback(grade_cog, mock_interaction, catch_id=1234)
    # Should handle exception and print
