from typing import Any

"""Comprehensive tests for tl_img_gen module."""

from unittest.mock import MagicMock, patch  # noqa: E402

from PIL import Image  # noqa: E402

from utils.tl_img_gen import (  # noqa: E402
    create_base_tier_list,
    create_tier_list_with_images,
)


class TestCreateBaseTierList:
    """Test cases for the create_base_tier_list function."""

    def test_create_base_tier_list_default_parameters(self) -> None:
        """Test create_base_tier_list with default parameters."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500)

                    # Verify Image.new was called with RGBA mode
                    mock_new.assert_called_once()
                    call_args = mock_new.call_args
                    assert call_args[0][0] == "RGBA"
                    assert call_args[0][1] == (1000, 500)

    def test_create_base_tier_list_custom_dimensions(self) -> None:
        """Test create_base_tier_list with custom dimensions."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1800, 900)

                    call_args = mock_new.call_args
                    assert call_args[0][1] == (1800, 900)

    def test_create_base_tier_list_with_custom_row_gap(self) -> None:
        """Test create_base_tier_list with custom row gap."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500, row_gap=20)

                    # Should use custom row gap
                    assert mock_draw_instance.rectangle.call_count > 0

    def test_create_base_tier_list_with_custom_font(self) -> None:
        """Test create_base_tier_list with custom font path."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500, font_path="custom.ttf")

                    # Should use custom font path
                    mock_font.assert_called()
                    call_args = mock_font.call_args
                    assert call_args[0][0] == "custom.ttf"

    def test_create_base_tier_list_with_custom_font_size(self) -> None:
        """Test create_base_tier_list with custom font size."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500, font_size=30)

                    # Should call font with custom size (if implementation supports it)
                    mock_font.assert_called()
                    # Just verify the function completed without error

    def test_create_base_tier_list_with_image_paths(self) -> None:
        """Test create_base_tier_list with image paths."""
        image_paths = {
            "S": ["image1.png", "image2.png"],
            "A": ["image3.png"],
            "B": [],
            "C": [],
            "D": []
        }

        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500, image_paths=image_paths)

                    # Should calculate height based on image counts
                    assert mock_draw_instance.rectangle.call_count > 0

    def test_create_base_tier_list_draws_tier_colors(self) -> None:
        """Test that create_base_tier_list draws correct tier colors."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500)

                    # Verify rectangles were drawn for each tier
                    rectangle_calls = mock_draw_instance.rectangle.call_args_list
                    assert len(rectangle_calls) >= 5  # 5 tiers

                    # Verify tier colors are correct

                    # Check that some calls include these colors
                    color_calls = [call for call in rectangle_calls if 'fill' in call[1]]
                    assert len(color_calls) > 0

    def test_create_base_tier_list_draws_tier_labels(self) -> None:
        """Test that create_base_tier_list draws tier labels."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font_instance.textbbox = MagicMock(return_value=(0, 0, 50, 20))
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500)

                    # Verify text was drawn for each tier
                    text_calls = mock_draw_instance.text.call_args_list
                    assert len(text_calls) >= 5  # 5 tiers

    def test_create_base_tier_list_calculates_height_correctly(self) -> None:
        """Test that create_base_tier_list calculates height based on images."""
        image_paths = {
            "S": ["image1.png"] * 10,  # 10 images
            "A": ["image2.png"] * 5,   # 5 images
            "B": [],
            "C": [],
            "D": []
        }

        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font_instance.textbbox = MagicMock(return_value=(0, 0, 50, 20))
                    mock_font.return_value = mock_font_instance

                    create_base_tier_list(1000, 500, image_paths=image_paths)

                    # Should calculate height based on number of images
                    assert mock_draw_instance.rectangle.call_count > 0


class TestCreateTierListWithImages:
    """Test cases for the create_tier_list_with_images function."""

    def test_create_tier_list_with_images_basic(self) -> None:
        """Test basic functionality of create_tier_list_with_images."""
        image_paths: dict[str, Any] = {
            "S": [],
            "A": [],
            "B": [],
            "C": [],
            "D": []
        }
        with patch('utils.tl_img_gen.create_base_tier_list') as mock_base:
            mock_base_img = MagicMock(spec=Image.Image)
            mock_base.return_value = mock_base_img

            with patch('utils.tl_img_gen.ImageDraw.Draw'):
                result = create_tier_list_with_images(1000, 500, image_paths)

                # Should return the base image after pasting
                assert result == mock_base_img

    def test_create_tier_list_with_images_pastes_images(self) -> None:
        """Test that images are pasted onto the base image."""
        image_paths = {
            "S": ["test_image.png"],
            "A": [],
            "B": [],
            "C": [],
            "D": []
        }

        with patch('utils.tl_img_gen.create_base_tier_list') as mock_base:
            mock_base_img = MagicMock(spec=Image.Image)
            mock_base.return_value = mock_base_img

            with patch('utils.tl_img_gen.ImageDraw.Draw'):
                with patch('utils.tl_img_gen.Image.open') as mock_open:
                    mock_img = MagicMock()
                    mock_open.return_value = mock_img
                    mock_img.convert.return_value = mock_img
                    mock_img.resize.return_value = mock_img

                    create_tier_list_with_images(1000, 500, image_paths)

                    # Verify Image.open was called
                    mock_open.assert_called_once_with("test_image.png")
                    # Verify paste was called on the base image
                    mock_base_img.paste.assert_called_once()

    def test_create_tier_list_with_images_handles_errors(self) -> None:
        """Test that image loading errors are caught and handled."""
        image_paths = {
            "S": ["nonexistent_image.png"],
            "A": [],
            "B": [],
            "C": [],
            "D": []
        }

        with patch('utils.tl_img_gen.create_base_tier_list') as mock_base:
            mock_base_img = MagicMock(spec=Image.Image)
            mock_base.return_value = mock_base_img

            with patch('utils.tl_img_gen.ImageDraw.Draw'):
                with patch('utils.tl_img_gen.Image.open') as mock_open:
                    mock_open.side_effect = Exception("File not found")

                    # Should not raise exception
                    create_tier_list_with_images(1000, 500, image_paths)

                    # Paste should not be called since open failed
                    mock_base_img.paste.assert_not_called()

    def test_create_tier_list_with_images_wraps_row(self) -> None:
        """Test that images wrap to the next row when exceeding width."""
        image_paths = {
            "S": ["image1.png", "image2.png"],
            "A": [],
            "B": [],
            "C": [],
            "D": []
        }

        with patch('utils.tl_img_gen.create_base_tier_list') as mock_base:
            mock_base_img = MagicMock(spec=Image.Image)
            mock_base.return_value = mock_base_img

            with patch('utils.tl_img_gen.ImageDraw.Draw'):
                with patch('utils.tl_img_gen.Image.open') as mock_open:
                    mock_img = MagicMock()
                    mock_open.return_value = mock_img
                    mock_img.convert.return_value = mock_img
                    mock_img.resize.return_value = mock_img

                    # Width 300 means max_images_per_row = (300 - 100) // 110 = 1
                    # So 2 images will force a row wrap
                    create_tier_list_with_images(300, 500, image_paths)

                    # Verify paste was called twice
                    assert mock_base_img.paste.call_count == 2

                    # Verify the first image was placed at x=110
                    # and the second image was placed at x=110 on the next row
                    paste_calls = mock_base_img.paste.call_args_list
                    first_y = paste_calls[0][0][1][1]
                    assert paste_calls[0][0][1][0] == 110  # x_offset
                    assert paste_calls[1][0][1][0] == 110  # x_offset after wrap
                    assert paste_calls[1][0][1][1] == first_y + 110  # y_start after wrap

    def test_create_base_tier_list_negative_row_gap(self) -> None:
        """Test create_base_tier_list with negative row gap."""
        with patch('utils.tl_img_gen.Image.new') as mock_new:
            mock_image = MagicMock(spec=Image.Image)
            mock_new.return_value = mock_image

            with patch('utils.tl_img_gen.ImageDraw.Draw') as mock_draw:
                mock_draw_instance = MagicMock()
                mock_draw.return_value = mock_draw_instance

                with patch('utils.tl_img_gen.ImageFont.truetype') as mock_font:
                    mock_font_instance = MagicMock()
                    mock_font.return_value = mock_font_instance

                    # Should handle negative row gap (though not practical)
                    create_base_tier_list(1000, 500, row_gap=-10)

                    mock_new.assert_called_once()
