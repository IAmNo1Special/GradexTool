from typing import Any
import unittest.mock
import json
import logging
import runpy
import pytest
from unittest.mock import patch, mock_open

from scripts.evolutions import get_evolutions

def test_get_evolutions_file_not_found() -> None:
    with patch("scripts.evolutions.REVOMON_FILE") as mock_revomon_file:
        mock_revomon_file.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            get_evolutions()

def test_get_evolutions_success() -> None:
    mock_data = [
        {"name": "A", "evolution": "B", "levelEvolution": 10},
        {"name": "B", "evolution": "", "levelEvolution": None},
        {"name": "C", "evolution": "D", "levelEvolution": 20}
    ]
    with patch("scripts.evolutions.REVOMON_FILE") as mock_revomon_file:
        mock_revomon_file.exists.return_value = True
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = get_evolutions(save_to_file=False)
            
            assert len(result) == 3
            assert result["1"]["from"] == "A"
            assert result["1"]["to"] == "B"
            
            assert result["2"]["from"] == "B"
            assert result["2"]["to"] is None

def test_get_evolutions_save_to_file() -> None:
    mock_data = [
        {"name": "A", "evolution": "B", "levelEvolution": 10}
    ]
    with patch("scripts.evolutions.REVOMON_FILE") as mock_revomon_file, \
         patch("scripts.evolutions.EVOLUTIONS_FILE") as mock_evolutions_file, \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_data))) as m_open:
        
        mock_revomon_file.exists.return_value = True
        
        result = get_evolutions(save_to_file=True)
        
        assert len(result) == 1
        mock_makedirs.assert_called_once_with(mock_evolutions_file.parent, exist_ok=True)
        m_open.assert_any_call(mock_evolutions_file, "w", encoding="utf-8")

def test_main() -> None:
    with patch("configs.REVOMON_FILE") as mock_revomon, \
         patch("configs.EVOLUTIONS_FILE"), \
         patch("os.makedirs"), \
         patch("builtins.open", mock_open(read_data='[]')):
        mock_revomon.exists.return_value = True
        with unittest.mock.patch.dict('sys.modules'):

            import sys

            sys.modules.pop('scripts.evolutions', None)

            runpy.run_module('scripts.evolutions', run_name='__main__')


