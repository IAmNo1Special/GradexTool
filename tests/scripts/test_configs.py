from typing import Any
import io
import logging
from unittest.mock import patch, MagicMock

import pytest

from scripts.configs import _get_configs
from scripts.configs.logging_config import setup_logging

def test_get_configs() -> None:
    yaml_data = "TEST_KEY: test_val\n"
    with patch("builtins.open", return_value=io.StringIO(yaml_data)):
        res = _get_configs()
        assert res == {"TEST_KEY": "test_val"}

@patch("scripts.configs.logging_config.Path")
@patch("scripts.configs.logging_config.RotatingFileHandler")
def test_setup_logging(mock_rfh: Any, mock_path: Any) -> None:
    mock_path_instance = mock_path.return_value
    
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    root_logger.handlers = []

    try:
        logger = setup_logging("TestLogger")
        assert logger.name == "TestLogger"
        assert len(root_logger.handlers) == 2
        mock_path_instance.parent.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_rfh.assert_called_once()
        
        # Test branch where handlers are already set
        logger2 = setup_logging("TestLogger2")
        assert logger2.name == "TestLogger2"
        assert len(root_logger.handlers) == 2
    finally:
        # Cleanup root logger
        root_logger.handlers = original_handlers
