import json
import logging
import os
import runpy
import sys
import unittest.mock
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.abspath("scripts"))
from scripts import items


def test_get_items(monkeypatch: Any, tmp_path: Any, caplog: Any) -> None:
    out_path = tmp_path / "items.json"
    monkeypatch.setattr(items, "OUTPUT_PATH", out_path)

    test_items = [
        {"name": "Potion", "description": "restores 20 hp.", "obtained_from": "RevoCenter", "cost": 200},
        {"cost": 100} # missing name, description, obtained_from
    ]
    monkeypatch.setattr(items, "ITEMS", test_items)

    with caplog.at_level(logging.INFO):
        items.get_items()

    assert out_path.exists()
    with open(out_path, encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 2
    assert data["1"]["cost"] == 100
    assert data["2"]["name"] == "potion"
    assert data["2"]["description"] == "Restores 20 hp."
    assert data["2"]["obtained_from"] == "revocenter"

def test_items_main(monkeypatch: Any) -> None:
    # Mock open so we don't write to the real file during runpy execution
    with patch("builtins.open"):
        with patch.dict("sys.modules", {"scripts.items": items}):
            with unittest.mock.patch.dict('sys.modules'):

                import sys

                sys.modules.pop('scripts.items', None)

                runpy.run_module('scripts.items', run_name='__main__')
