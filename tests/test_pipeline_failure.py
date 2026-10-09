
from unittest.mock import patch

import pytest

from main import run_pipeline


def test_pipeline_stops_when_extraction_fails():
    # Simulasi API gagal mengirim data
    with (
        patch("main.extract_stock") as mock_extract,
        patch("main.transform_stock") as mock_transform,
        patch("main.validate_stock") as mock_validate,
        patch("main.load_stock") as mock_load,
    ):
        mock_extract.side_effect = RuntimeError(
            "Simulated API failure"
        )

        with pytest.raises(RuntimeError, match="Simulated API failure"):
            run_pipeline("AAPL")

        mock_transform.assert_not_called()
        mock_validate.assert_not_called()
        mock_load.assert_not_called()


def test_pipeline_stops_when_validation_fails():
    # Simulasi data saham gagal validasi
    with (
        patch("main.extract_stock") as mock_extract,
        patch("main.transform_stock") as mock_transform,
        patch("main.validate_stock") as mock_validate,
        patch("main.load_stock") as mock_load,
    ):
        mock_validate.return_value = False

        with pytest.raises(ValueError, match="Validation failed for AAPL"):
            run_pipeline("AAPL")

        mock_extract.assert_called_once_with("AAPL")
        mock_transform.assert_called_once_with("AAPL")
        mock_validate.assert_called_once_with("AAPL")
        mock_load.assert_not_called()


def test_pipeline_rolls_forward_when_all_steps_pass():
    # Simulasi seluruh proses berhasil
    with (
        patch("main.extract_stock") as mock_extract,
        patch("main.transform_stock") as mock_transform,
        patch("main.validate_stock") as mock_validate,
        patch("main.load_stock") as mock_load,
    ):
        mock_validate.return_value = True
        mock_load.return_value = {
            "new": 0,
            "changed": 0,
            "unchanged": 100
        }

        run_pipeline("AAPL")

        mock_extract.assert_called_once_with("AAPL")
        mock_transform.assert_called_once_with("AAPL")
        mock_validate.assert_called_once_with("AAPL")
        mock_load.assert_called_once_with("AAPL")
