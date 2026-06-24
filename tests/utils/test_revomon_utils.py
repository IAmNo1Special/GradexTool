from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from utils.revomon_utils import (
    appraise_revomon,
    create_graded_mon_img,
    evaluate_stat_iv,
    get_attributes,
    get_book_of_land_ids,
    get_book_of_mon_names,
    get_evo_trees,
    get_grade,
    get_nature_mods,
    get_natures,
    get_perferred_natures,
    get_stat_weights,
    save_mon_imgs,
    save_type_imgs,
)


@pytest.fixture
def mock_tables() -> None:  # type: ignore[misc]
    with patch("utils.revomon_utils.RevomonTable") as rt, \
         patch("utils.revomon_utils.TypesTable") as tt, \
         patch("utils.revomon_utils.RevomonMovesTable") as rmt, \
         patch("utils.revomon_utils.CounterdexTable") as ct, \
         patch("utils.revomon_utils.NaturesTable") as nt, \
         patch("utils.revomon_utils.OwnedLandsTable") as olt:
        yield rt, tt, rmt, ct, nt, olt

@pytest.mark.asyncio
async def test_get_attributes(mock_tables: Any) -> None:
    rt, tt, rmt, ct, nt, olt = mock_tables
    mock_mon_info = [0] * 43
    mock_mon_info[0] = 1
    mock_mon_info[2] = "Pikachu"
    mock_mon_info[3] = "Desc"
    mock_mon_info[4] = "Electric"
    mock_mon_info[6] = "Ability1"
    mock_mon_info[7] = "Ability2"
    mock_mon_info[8] = "AbilityH"
    mock_mon_info[9] = 35
    mock_mon_info[10] = 55
    mock_mon_info[11] = 40
    mock_mon_info[12] = 50
    mock_mon_info[13] = 50
    mock_mon_info[14] = 90
    mock_mon_info[15] = "Raichu"
    mock_mon_info[16] = "Lvl 20"
    mock_mon_info[17] = "Rare"
    mock_mon_info[28] = 2
    rt.return_value.get_info = AsyncMock(return_value=[mock_mon_info])
    tt.return_value.get_info = AsyncMock(return_value=[["type1", "chart_img_url"]])
    rmt.return_value.get_moves_for_revomon = AsyncMock(return_value=[["Thunderbolt"]])
    ct.return_value.get_info = AsyncMock(return_value=[[0, 1, 2, "cdex desc", "Tier 1", "Thunderbolt", "Modest", "tips", "counters", "Ground"]])

    attr = await get_attributes("pikachu")
    assert attr["name"] == "Pikachu"
    assert attr["base_spe"] == 90

@pytest.mark.asyncio
async def test_get_attributes_multiple_evs(mock_tables: Any) -> None:
    rt, tt, rmt, ct, nt, olt = mock_tables
    mock_mon_info = [0] * 43
    mock_mon_info[2] = "Bulbasaur"  # type: ignore[call-overload]
    mock_mon_info[23] = 1 # HP
    mock_mon_info[25] = 1 # Def

    rt.return_value.get_info = AsyncMock(return_value=[mock_mon_info])
    tt.return_value.get_info = AsyncMock(return_value=[["type1", "chart_img_url"]])
    rmt.return_value.get_moves_for_revomon = AsyncMock(return_value=[])
    ct.return_value.get_info = AsyncMock(return_value=[[0] * 10])

    attr = await get_attributes("bulbasaur")
    assert attr["ev_gains1"] == "+ 1 Hit Points"
    assert attr["ev_gains2"] == "+ 1 Defense "

@patch("utils.revomon_utils.requests.get")
@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_save_mon_imgs(mock_get_attributes: Any, mock_requests_get: Any, mock_tables: Any) -> None:
    rt = mock_tables[0]
    rt.return_value.get_names = AsyncMock(return_value=["pikachu"])
    mock_get_attributes.return_value = {
        "profile_img": "url1", "shiny_profile_img": "url2",
        "nft_img": "url3", "shiny_nft_img": "url4"
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"image_data"
    mock_requests_get.return_value = mock_response

    m_open = mock_open()
    m_open.side_effect = [FileNotFoundError, m_open.return_value] * 4

    with patch("builtins.open", m_open):
        await save_mon_imgs()

@patch("utils.revomon_utils.requests.get")
@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_save_mon_imgs_exists(mock_get_attributes: Any, mock_requests_get: Any, mock_tables: Any) -> None:
    rt = mock_tables[0]
    rt.return_value.get_names = AsyncMock(return_value=["pikachu"])
    mock_get_attributes.return_value = {
        "profile_img": "url1", "shiny_profile_img": "url2",
        "nft_img": "url3", "shiny_nft_img": "url4"
    }
    m_open = mock_open()
    with patch("builtins.open", m_open):
        await save_mon_imgs()

@patch("utils.revomon_utils.requests.get")
@pytest.mark.asyncio
async def test_save_type_imgs(mock_requests_get: Any, mock_tables: Any) -> None:
    tt = mock_tables[1]
    tt.return_value.get_mono_types = AsyncMock(return_value=["Electric"])
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"image_data"
    mock_requests_get.return_value = mock_response

    m_open = mock_open()
    m_open.side_effect = [FileNotFoundError, m_open.return_value]
    with patch("builtins.open", m_open):
        await save_type_imgs()

@patch("utils.revomon_utils.requests.get")
@pytest.mark.asyncio
async def test_save_type_imgs_exists(mock_requests_get: Any, mock_tables: Any) -> None:
    tt = mock_tables[1]
    tt.return_value.get_mono_types = AsyncMock(return_value=["Electric"])
    m_open = mock_open()
    with patch("builtins.open", m_open):
        await save_type_imgs()

@pytest.mark.asyncio
async def test_get_natures(mock_tables: Any) -> None:
    nt = mock_tables[4]
    nt.return_value.get_names = AsyncMock(return_value=["Adamant", "Bold"])
    assert await get_natures() == ["Adamant", "Bold"]

def test_get_nature_mods_all() -> None:
    # Test every single branch of nature logic
    assert get_nature_mods("Adamant")["atk"] == 1.1
    assert get_nature_mods("Brave")["atk"] == 1.1
    assert get_nature_mods("Lonely")["atk"] == 1.1
    assert get_nature_mods("Naughty")["atk"] == 1.1

    assert get_nature_mods("Bold")["def"] == 1.1
    assert get_nature_mods("Impish")["def"] == 1.1
    assert get_nature_mods("Lax")["def"] == 1.1
    assert get_nature_mods("Relaxed")["def"] == 1.1

    assert get_nature_mods("Modest")["spa"] == 1.1
    assert get_nature_mods("Mild")["spa"] == 1.1
    assert get_nature_mods("Quiet")["spa"] == 1.1
    assert get_nature_mods("Rash")["spa"] == 1.1

    assert get_nature_mods("Calm")["spd"] == 1.1
    assert get_nature_mods("Careful")["spd"] == 1.1
    assert get_nature_mods("Gentle")["spd"] == 1.1
    assert get_nature_mods("Sassy")["spd"] == 1.1

    assert get_nature_mods("Hasty")["spe"] == 1.1
    assert get_nature_mods("Jolly")["spe"] == 1.1
    assert get_nature_mods("Naive")["spe"] == 1.1
    assert get_nature_mods("Timid")["spe"] == 1.1

    # Drops
    assert get_nature_mods("Bold")["atk"] == 0.9
    assert get_nature_mods("Modest")["atk"] == 0.9
    assert get_nature_mods("Calm")["atk"] == 0.9
    assert get_nature_mods("Timid")["atk"] == 0.9

    assert get_nature_mods("Lonely")["def"] == 0.9
    assert get_nature_mods("Mild")["def"] == 0.9
    assert get_nature_mods("Gentle")["def"] == 0.9
    assert get_nature_mods("Hasty")["def"] == 0.9

    assert get_nature_mods("Adamant")["spa"] == 0.9
    assert get_nature_mods("Impish")["spa"] == 0.9
    assert get_nature_mods("Careful")["spa"] == 0.9
    assert get_nature_mods("Jolly")["spa"] == 0.9

    assert get_nature_mods("Naughty")["spd"] == 0.9
    assert get_nature_mods("Lax")["spd"] == 0.9
    assert get_nature_mods("Rash")["spd"] == 0.9
    assert get_nature_mods("Naive")["spd"] == 0.9

    assert get_nature_mods("Brave")["spe"] == 0.9
    assert get_nature_mods("Relaxed")["spe"] == 0.9
    assert get_nature_mods("Quiet")["spe"] == 0.9
    assert get_nature_mods("Sassy")["spe"] == 0.9

@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@patch("utils.revomon_utils.get_natures", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_perferred_natures(mock_get_natures: Any, mock_get_attributes: Any) -> None:
    mock_get_natures.return_value = ["Adamant", "Jolly", "Modest"]
    mock_get_attributes.return_value = {"meta_build": "Adamant, Jolly"}
    assert await get_perferred_natures("pikachu") == ["Adamant", "Jolly"]

@patch("utils.revomon_utils.requests.post")
def test_get_evo_trees(mock_post: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"revomons": [
        {"idRevodex": 1, "name": "Vyphern", "evolution": "Wyverdant", "levelEvolution": 30},
        {"idRevodex": 2, "name": "Wyverdant", "evolution": "", "levelEvolution": 0},
        {"idRevodex": 3, "name": "Pichu", "evolution": "Pikachu", "levelEvolution": 10},
        {"idRevodex": 4, "name": "Pikachu", "evolution": "Raichu", "levelEvolution": 20},
        {"idRevodex": 5, "name": "Raichu", "evolution": "", "levelEvolution": 0},
    ]}}
    mock_post.return_value = mock_response
    trees = get_evo_trees()
    assert len(trees) == 2
    assert any("Vyphern" in t and "Wyverdant" in t for t in trees)
    assert any("Pichu" in t and "Pikachu" in t and "Raichu" in t for t in trees)

@patch("utils.revomon_utils.requests.post")
def test_get_evo_trees_wyverdant(mock_post: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"revomons": [
        {"idRevodex": 2, "name": "Wyverdant", "evolution": "", "levelEvolution": 0},
    ]}}
    mock_post.return_value = mock_response
    trees = get_evo_trees()
    assert len(trees) == 0

@patch("utils.revomon_utils.requests.post")
def test_get_evo_trees_standalone(mock_post: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"revomons": [
        {"idRevodex": 10, "name": "Tauros", "evolution": "", "levelEvolution": 0},
    ]}}
    mock_post.return_value = mock_response
    trees = get_evo_trees()
    assert len(trees) == 1
    assert "| Tauros |\n" in trees

@patch("utils.revomon_utils.requests.post")
def test_get_evo_trees_non_200(mock_post: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_post.return_value = mock_response
    assert get_evo_trees() == []

@pytest.mark.asyncio
async def test_get_book_of_mon_names(mock_tables: Any) -> None:
    rt = mock_tables[0]
    rt.return_value.get_names = AsyncMock(return_value=["A", "B", "C", "D", "E", "vyphern", "wyverdant", "F"])
    def mock_get_info(name: Any) -> Any:
        return [[0, 1, 2, 3, 4, 5, 6, 7, None]]
    rt.return_value.get_info = AsyncMock(side_effect=mock_get_info)
    book = await get_book_of_mon_names()
    assert book is not None

@pytest.mark.asyncio
async def test_get_book_of_land_ids(mock_tables: Any) -> None:
    olt = mock_tables[5]
    olt.return_value.get_ids = AsyncMock(return_value=list(range(1, 14)))
    book = await get_book_of_land_ids()
    assert len(book) == 2

def test_get_grade() -> None:
    assert get_grade(95.0) == "A+"
    assert get_grade(85.0) == "A"
    assert get_grade(75.0) == "B"
    assert get_grade(65.0) == "C"
    assert get_grade(45.0) == "D"
    assert get_grade(35.0) == "F"
    assert get_grade(20.0) == "F-"
    assert get_grade(-1.0) == ""

def test_get_stat_weights() -> None:
    w, r = get_stat_weights({"base_atk": 120, "base_spa": 50, "base_spe": 110})
    assert r == "Fast Physical Attacker"

    w, r = get_stat_weights({"base_spa": 120, "base_atk": 50, "base_spe": 40})
    assert r == "Slow Special Attacker"

    w, r = get_stat_weights({"base_def": 120, "base_spd": 100, "base_spe": 60})
    assert r == "Defensive Balanced"
    assert w["def"] == 1.8
    assert w["spd"] == 1.2

    w, r = get_stat_weights({"base_spd": 120, "base_def": 100, "base_hp": 120, "base_spe": 60})
    assert r == "Defensive Balanced"
    assert w["spd"] == 1.8
    assert w["def"] == 1.2
    assert w["hp"] == 1.5

    w, r = get_stat_weights({"base_atk": 100, "base_spa": 100, "base_spe": 80})
    assert r == "Mixed Attacker"
    assert w["atk"] == 1.5
    assert w["spa"] == 1.5

def test_evaluate_stat_iv() -> None:
    assert evaluate_stat_iv("atk", 4, 0.1, "Special Attacker") == 31
    assert evaluate_stat_iv("atk", 10, 0.1, "Special Attacker") == 21
    assert evaluate_stat_iv("spe", 0, 0.5, "Slow Balanced") == 0

@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_appraise_revomon(mock_get_attributes: Any) -> None:
    mock_get_attributes.return_value = {"base_atk": 120, "base_spa": 50, "base_spe": 110}
    stats = {
        "mon_name": "Pikachu", "mon_nature": "Adamant", "mon_ability": "Static",
        "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31
    }
    res = await appraise_revomon(stats)
    assert res["nature_quality"] == "Perfect"  # type: ignore[index]

@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_appraise_revomon_poor_nature(mock_get_attributes: Any) -> None:
    mock_get_attributes.return_value = {"base_atk": 120, "base_spa": 50, "base_spe": 110}
    stats = {
        "mon_name": "Pikachu", "mon_nature": "Modest", "mon_ability": "Static",
        "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31
    }
    res = await appraise_revomon(stats)
    assert res["nature_quality"] == "Poor"  # type: ignore[index]

@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_appraise_revomon_good_nature(mock_get_attributes: Any) -> None:
    mock_get_attributes.return_value = {"base_atk": 100, "base_spa": 100, "base_spe": 100}
    stats = {
        "mon_name": "Pikachu", "mon_nature": "Mild", "mon_ability": "Static",
        "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31
    }
    res = await appraise_revomon(stats)
    assert res["nature_quality"] == "Good"  # type: ignore[index]

@patch("utils.revomon_utils.get_attributes", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_appraise_revomon_exception(mock_get_attributes: Any) -> None:
    mock_get_attributes.side_effect = Exception("error")
    stats = {
        "mon_name": "Pikachu", "mon_nature": "Adamant", "mon_ability": "Static",
        "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31
    }
    res = await appraise_revomon(stats)
    assert res is None

@patch("utils.revomon_utils.Image.open")
@patch("utils.revomon_utils.Image.new")
@patch("utils.revomon_utils.ImageDraw.Draw")
@patch("utils.revomon_utils.ImageFont.truetype")
@patch("utils.revomon_utils.go.Figure")
def test_create_graded_mon_img(mock_figure: Any, mock_truetype: Any, mock_draw: Any, mock_new: Any, mock_open: Any) -> None:
    mock_image_instance = MagicMock()
    mock_image_instance.width = 100
    mock_image_instance.height = 100
    mock_image_instance.size = (750, 1050)
    mock_open.return_value = mock_image_instance
    mock_new.return_value = mock_image_instance

    mock_draw_instance = MagicMock()
    mock_draw.return_value = mock_draw_instance
    mock_draw_instance.textbbox.return_value = (0, 0, 50, 20)

    stats = {
        "mon_name": "Pikachu", "mon_nature": "Adamant", "mon_ability": "Static",
        "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31,
        "shiny": False, "grade_letter": "A+", "catch_id": 12345
    }
    img = create_graded_mon_img(stats, score_percentage=95.0)
    assert img == mock_image_instance

@patch("utils.revomon_utils.Image.open")
@patch("utils.revomon_utils.Image.new")
@patch("utils.revomon_utils.ImageDraw.Draw")
@patch("utils.revomon_utils.ImageFont.truetype")
@patch("utils.revomon_utils.go.Figure")
def test_create_graded_mon_img_os_error_font_and_image(mock_figure: Any, mock_truetype: Any, mock_draw: Any, mock_new: Any, mock_open: Any) -> None:
    mock_image_instance = MagicMock()
    mock_image_instance.width = 100
    mock_image_instance.height = 100
    mock_image_instance.size = (750, 1050)
    mock_new.return_value = mock_image_instance

    mock_truetype.side_effect = [OSError("No font"), MagicMock()]

    def open_side_effect(path: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(path, str) and path.endswith('.png'):
            if "shiny-" in path or "Pikachu.png" in path:
                raise OSError("No image")
        return mock_image_instance
    mock_open.side_effect = open_side_effect

    mock_draw_instance = MagicMock()
    mock_draw.return_value = mock_draw_instance
    mock_draw_instance.textbbox.return_value = (0, 0, 50, 20)

    stats = {
        "mon_name": "Pikachu", "mon_nature": "Adamant", "mon_ability": "Static",
        "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31,
        "shiny": True, "grade_letter": "A", "catch_id": 12345
    }
    with patch("utils.revomon_utils.ImageFont.load_default") as mock_default:
        mock_default.return_value = MagicMock()
        img = create_graded_mon_img(stats, score_percentage=85.0)
        assert img == mock_image_instance

@patch("utils.revomon_utils.Image.open")
@patch("utils.revomon_utils.Image.new")
@patch("utils.revomon_utils.ImageDraw.Draw")
@patch("utils.revomon_utils.ImageFont.truetype")
@patch("utils.revomon_utils.go.Figure")
def test_create_graded_mon_img_grades(mock_figure: Any, mock_truetype: Any, mock_draw: Any, mock_new: Any, mock_open: Any) -> None:
    mock_image_instance = MagicMock()
    mock_image_instance.width = 100
    mock_image_instance.height = 100
    mock_image_instance.size = (750, 1050)
    mock_open.return_value = mock_image_instance
    mock_new.return_value = mock_image_instance

    mock_draw_instance = MagicMock()
    mock_draw.return_value = mock_draw_instance
    mock_draw_instance.textbbox.return_value = (0, 0, 50, 20)

    for grade in ["A", "B", "C", "D", "F", "F-"]:
        stats = {
            "mon_name": "Pikachu", "mon_nature": "Adamant", "mon_ability": "Static",
            "hp_iv": 31, "atk_iv": 31, "def_iv": 31, "spa_iv": 31, "spd_iv": 31, "spe_iv": 31,
            "shiny": False, "grade_letter": grade, "catch_id": 12345
        }
        create_graded_mon_img(stats, score_percentage=85.0)
