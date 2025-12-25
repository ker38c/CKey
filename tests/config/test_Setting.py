import pytest
import os
import tempfile
import shutil
from unittest import mock

from src.config.Setting import (
    GuiSetting, Setting,
    MIN_WIDTH, MAX_WIDTH, DEFAULT_WIDTH,
    MIN_HEIGHT, MAX_HEIGHT, DEFAULT_HEIGHT,
    DEFAULT_KEY_PUSHED_COLOR, DEFAULT_ENABLE_MIDI_FILE,
    DEFAULT_SHOW_IMAGE_FRAME,
    round
)


class TestRoundFunction:
    """Test the round utility function."""
    
    def test_round_within_range(self):
        # Arrange
        value = 1500
        min_val = 400
        max_val = 4000
        
        # Act
        result = round(value, min_val, max_val)
        
        # Assert
        assert result == 1500

    def test_round_below_minimum(self):
        # Arrange
        value = 100
        min_val = 400
        max_val = 4000
        
        # Act
        result = round(value, min_val, max_val)
        
        # Assert
        assert result == 400

    def test_round_above_maximum(self):
        # Arrange
        value = 5000
        min_val = 400
        max_val = 4000
        
        # Act
        result = round(value, min_val, max_val)
        
        # Assert
        assert result == 4000

    def test_round_at_minimum_boundary(self):
        # Arrange
        value = 400
        min_val = 400
        max_val = 4000
        
        # Act
        result = round(value, min_val, max_val)
        
        # Assert
        assert result == 400

    def test_round_at_maximum_boundary(self):
        # Arrange
        value = 4000
        min_val = 400
        max_val = 4000
        
        # Act
        result = round(value, min_val, max_val)
        
        # Assert
        assert result == 4000


class TestGuiSettingInitialization:
    """Test GuiSetting initialization."""
    
    def test_gui_setting_default_values(self):
        # Arrange & Act
        gui_setting = GuiSetting()
        
        # Assert
        assert gui_setting.Width == DEFAULT_WIDTH
        assert gui_setting.Height == DEFAULT_HEIGHT
        assert gui_setting.KeyPushedColor == DEFAULT_KEY_PUSHED_COLOR
        assert gui_setting.EnableMidiFile == DEFAULT_ENABLE_MIDI_FILE
        assert gui_setting.ImagePath == ""
        assert gui_setting.ShowImageFrame == DEFAULT_SHOW_IMAGE_FRAME


class TestGuiSettingWidth:
    """Test GuiSetting Width property."""
    
    def test_width_valid_integer(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Width = 1000
        
        # Assert
        assert gui_setting.Width == 1000

    def test_width_string_conversion(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Width = "1500"
        
        # Assert
        assert gui_setting.Width == 1500

    def test_width_clamps_below_minimum(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Width = 100
        
        # Assert
        assert gui_setting.Width == MIN_WIDTH

    def test_width_clamps_above_maximum(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Width = 5000
        
        # Assert
        assert gui_setting.Width == MAX_WIDTH

    def test_width_invalid_string_defaults_to_default_width(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Width = "invalid"
        
        # Assert
        assert gui_setting.Width == DEFAULT_WIDTH

    def test_width_none_defaults_to_default_width(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Width = None
        
        # Assert
        assert gui_setting.Width == DEFAULT_WIDTH


class TestGuiSettingHeight:
    """Test GuiSetting Height property."""
    
    def test_height_valid_integer(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Height = 600
        
        # Assert
        assert gui_setting.Height == 600

    def test_height_string_conversion(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Height = "800"
        
        # Assert
        assert gui_setting.Height == 800

    def test_height_clamps_below_minimum(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Height = 100
        
        # Assert
        assert gui_setting.Height == MIN_HEIGHT

    def test_height_clamps_above_maximum(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Height = 5000
        
        # Assert
        assert gui_setting.Height == MAX_HEIGHT

    def test_height_invalid_string_defaults_to_default_height(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Height = "invalid"
        
        # Assert
        assert gui_setting.Height == DEFAULT_HEIGHT

    def test_height_none_defaults_to_default_height(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.Height = None
        
        # Assert
        assert gui_setting.Height == DEFAULT_HEIGHT


class TestGuiSettingKeyPushedColor:
    """Test GuiSetting KeyPushedColor property."""
    
    def test_key_pushed_color_default_value(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act & Assert
        assert gui_setting.KeyPushedColor == DEFAULT_KEY_PUSHED_COLOR

    def test_key_pushed_color_set_custom_color(self):
        # Arrange
        gui_setting = GuiSetting()
        custom_color = "red"
        
        # Act
        gui_setting.KeyPushedColor = custom_color
        
        # Assert
        assert gui_setting.KeyPushedColor == custom_color

    def test_key_pushed_color_set_hex_color(self):
        # Arrange
        gui_setting = GuiSetting()
        hex_color = "#FF0000"
        
        # Act
        gui_setting.KeyPushedColor = hex_color
        
        # Assert
        assert gui_setting.KeyPushedColor == hex_color


class TestGuiSettingEnableMidiFile:
    """Test GuiSetting EnableMidiFile property."""
    
    def test_enable_midi_file_default_value(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act & Assert
        assert gui_setting.EnableMidiFile == DEFAULT_ENABLE_MIDI_FILE

    def test_enable_midi_file_set_bool_true(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = True
        
        # Assert
        assert gui_setting.EnableMidiFile is True

    def test_enable_midi_file_set_bool_false(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = False
        
        # Assert
        assert gui_setting.EnableMidiFile is False

    def test_enable_midi_file_string_true(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = "true"
        
        # Assert
        assert gui_setting.EnableMidiFile is True

    def test_enable_midi_file_string_true_uppercase(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = "TRUE"
        
        # Assert
        assert gui_setting.EnableMidiFile is True

    def test_enable_midi_file_string_1(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = "1"
        
        # Assert
        assert gui_setting.EnableMidiFile is True

    def test_enable_midi_file_string_yes(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = "yes"
        
        # Assert
        assert gui_setting.EnableMidiFile is True

    def test_enable_midi_file_string_false(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = "false"
        
        # Assert
        assert gui_setting.EnableMidiFile is False

    def test_enable_midi_file_string_0(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = "0"
        
        # Assert
        assert gui_setting.EnableMidiFile is False

    def test_enable_midi_file_int_nonzero(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = 1
        
        # Assert
        assert gui_setting.EnableMidiFile is True

    def test_enable_midi_file_int_zero(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.EnableMidiFile = 0
        
        # Assert
        assert gui_setting.EnableMidiFile is False


class TestGuiSettingImagePath:
    """Test GuiSetting ImagePath property."""
    
    def test_image_path_default_value(self):
        # Arrange & Act
        gui_setting = GuiSetting()
        
        # Assert
        assert gui_setting.ImagePath == ""

    def test_image_path_set_string(self):
        # Arrange
        gui_setting = GuiSetting()
        test_path = "/path/to/image.png"
        
        # Act
        gui_setting.ImagePath = test_path
        
        # Assert
        assert gui_setting.ImagePath == test_path

    def test_image_path_set_windows_path(self):
        # Arrange
        gui_setting = GuiSetting()
        test_path = "C:\\Users\\test\\image.jpg"
        
        # Act
        gui_setting.ImagePath = test_path
        
        # Assert
        assert gui_setting.ImagePath == test_path

    def test_image_path_set_none(self):
        # Arrange
        gui_setting = GuiSetting()
        gui_setting.ImagePath = "/some/path.png"
        
        # Act
        gui_setting.ImagePath = None
        
        # Assert
        assert gui_setting.ImagePath == ""

    def test_image_path_set_empty_string(self):
        # Arrange
        gui_setting = GuiSetting()
        gui_setting.ImagePath = "/some/path.png"
        
        # Act
        gui_setting.ImagePath = ""
        
        # Assert
        assert gui_setting.ImagePath == ""

    def test_image_path_decode_utf8_bytes(self):
        # Arrange
        gui_setting = GuiSetting()
        test_path = "/path/to/画像.png"
        path_bytes = test_path.encode('utf-8')
        
        # Act
        gui_setting.ImagePath = path_bytes
        
        # Assert
        assert gui_setting.ImagePath == test_path

    def test_image_path_decode_cp932_bytes(self):
        # Arrange
        gui_setting = GuiSetting()
        test_path = "C:\\ユーザー\\画像.png"
        
        try:
            path_bytes = test_path.encode('cp932')
            
            # Act
            gui_setting.ImagePath = path_bytes
            
            # Assert
            assert gui_setting.ImagePath == test_path
        except UnicodeEncodeError:
            # Skip test if test string cannot be encoded in cp932
            pytest.skip("Test string cannot be encoded in cp932")

    def test_image_path_decode_invalid_bytes_fallback(self):
        # Arrange
        gui_setting = GuiSetting()
        # Create bytes that are not valid UTF-8 or cp932
        invalid_bytes = b'\xff\xfe\xfd'
        
        # Act
        gui_setting.ImagePath = invalid_bytes
        
        # Assert - Should not raise exception, returns empty or partial string
        assert isinstance(gui_setting.ImagePath, str)

    def test_image_path_int_conversion_to_string(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ImagePath = 12345
        
        # Assert
        assert gui_setting.ImagePath == "12345"


class TestGuiSettingShowImageFrame:
    """Test GuiSetting ShowImageFrame property."""
    
    def test_show_image_frame_default_value(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act & Assert
        assert gui_setting.ShowImageFrame == DEFAULT_SHOW_IMAGE_FRAME

    def test_show_image_frame_set_bool_true(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = True
        
        # Assert
        assert gui_setting.ShowImageFrame is True

    def test_show_image_frame_set_bool_false(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = False
        
        # Assert
        assert gui_setting.ShowImageFrame is False

    def test_show_image_frame_string_true(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = "true"
        
        # Assert
        assert gui_setting.ShowImageFrame is True

    def test_show_image_frame_string_true_uppercase(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = "TRUE"
        
        # Assert
        assert gui_setting.ShowImageFrame is True

    def test_show_image_frame_string_1(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = "1"
        
        # Assert
        assert gui_setting.ShowImageFrame is True

    def test_show_image_frame_string_yes(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = "yes"
        
        # Assert
        assert gui_setting.ShowImageFrame is True

    def test_show_image_frame_string_false(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = "false"
        
        # Assert
        assert gui_setting.ShowImageFrame is False

    def test_show_image_frame_string_0(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = "0"
        
        # Assert
        assert gui_setting.ShowImageFrame is False

    def test_show_image_frame_int_nonzero(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = 1
        
        # Assert
        assert gui_setting.ShowImageFrame is True

    def test_show_image_frame_int_zero(self):
        # Arrange
        gui_setting = GuiSetting()
        
        # Act
        gui_setting.ShowImageFrame = 0
        
        # Assert
        assert gui_setting.ShowImageFrame is False


class TestSettingInitialization:
    """Test Setting initialization with config file handling."""
    
    def test_setting_initializes_with_new_config_file(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Act
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
            
            # Assert
            assert os.path.exists(config_path)
            assert setting.gui is not None
            assert isinstance(setting.gui, GuiSetting)
        finally:
            shutil.rmtree(temp_dir)

    def test_setting_initializes_with_existing_config_file(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Create initial config
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting1 = Setting()
                setting1.gui.Width = 1200
                setting1.save_setting()
            
            # Act - Create new instance and load
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting2 = Setting()
            
            # Assert
            assert setting2.gui.Width == 1200
        finally:
            shutil.rmtree(temp_dir)


class TestSettingLoadSave:
    """Test Setting load and save functionality."""
    
    def test_load_setting_from_config_file(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Create initial setting
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting1 = Setting()
                setting1.gui.Width = 1200
                setting1.gui.Height = 600
                setting1.gui.KeyPushedColor = "yellow"
                setting1.save_setting()
            
            # Act - Load in new instance
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting2 = Setting()
            
            # Assert
            assert setting2.gui.Width == 1200
            assert setting2.gui.Height == 600
            assert setting2.gui.KeyPushedColor == "yellow"
        finally:
            shutil.rmtree(temp_dir)

    def test_save_setting_persists_to_file(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
                
                # Act
                setting.gui.Width = 1400
                setting.gui.Height = 700
                setting.save_setting()
            
            # Assert - Verify file content by reading directly
            import configparser
            parser = configparser.ConfigParser()
            parser.read(config_path, encoding="utf-8")
            
            assert parser["GUI"]["Width"] == "1400"
            assert parser["GUI"]["Height"] == "700"
        finally:
            shutil.rmtree(temp_dir)

    def test_save_setting_all_properties(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
                
                # Act
                setting.gui.Width = 1300
                setting.gui.Height = 650
                setting.gui.KeyPushedColor = "purple"
                setting.gui.EnableMidiFile = False
                setting.gui.ImagePath = "/path/to/image.png"
                setting.gui.ShowImageFrame = False
                setting.save_setting()
            
            # Assert
            import configparser
            parser = configparser.ConfigParser()
            parser.read(config_path, encoding="utf-8")
            
            assert parser["GUI"]["Width"] == "1300"
            assert parser["GUI"]["Height"] == "650"
            assert parser["GUI"]["KeyPushedColor"] == "purple"
            assert parser["GUI"]["EnableMidiFile"] == "False"
            assert parser["GUI"]["ImagePath"] == "/path/to/image.png"
            assert parser["GUI"]["ShowImageFrame"] == "False"
        finally:
            shutil.rmtree(temp_dir)

    def test_load_setting_with_missing_enable_midi_file(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Create config without EnableMidiFile
            import configparser
            parser = configparser.ConfigParser()
            parser["GUI"] = {
                "Width": "1000",
                "Height": "500",
                "KeyPushedColor": "blue"
            }
            with open(config_path, 'w') as f:
                parser.write(f)
            
            # Act
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
            
            # Assert - Should use default value
            assert setting.gui.EnableMidiFile == DEFAULT_ENABLE_MIDI_FILE
        finally:
            shutil.rmtree(temp_dir)

    def test_load_setting_with_missing_image_path(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Create config without ImagePath
            import configparser
            parser = configparser.ConfigParser()
            parser["GUI"] = {
                "Width": "1000",
                "Height": "500",
                "KeyPushedColor": "blue",
                "EnableMidiFile": "True"
            }
            with open(config_path, 'w') as f:
                parser.write(f)
            
            # Act
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
            
            # Assert - Should use default value (empty string)
            assert setting.gui.ImagePath == ""
        finally:
            shutil.rmtree(temp_dir)

    def test_load_setting_with_missing_show_image_frame(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Create config without ShowImageFrame
            import configparser
            parser = configparser.ConfigParser()
            parser["GUI"] = {
                "Width": "1000",
                "Height": "500",
                "KeyPushedColor": "blue",
                "EnableMidiFile": "True"
            }
            with open(config_path, 'w') as f:
                parser.write(f)
            
            # Act
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
            
            # Assert - Should use default value
            assert setting.gui.ShowImageFrame == DEFAULT_SHOW_IMAGE_FRAME
        finally:
            shutil.rmtree(temp_dir)

    def test_load_setting_with_image_path(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        test_path = "/home/user/image.png"
        
        try:
            # Create config with ImagePath
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting1 = Setting()
                setting1.gui.ImagePath = test_path
                setting1.save_setting()
            
            # Act - Load in new instance
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting2 = Setting()
            
            # Assert
            assert setting2.gui.ImagePath == test_path
        finally:
            shutil.rmtree(temp_dir)

    def test_load_setting_with_show_image_frame(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            # Create config with ShowImageFrame set to False
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting1 = Setting()
                setting1.gui.ShowImageFrame = False
                setting1.save_setting()
            
            # Act - Load in new instance
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting2 = Setting()
            
            # Assert
            assert setting2.gui.ShowImageFrame is False
        finally:
            shutil.rmtree(temp_dir)


class TestSettingDefaultConfig:
    """Test Setting default configuration creation."""
    
    def test_create_default_setting_creates_file(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
                
                # Act
                setting.create_default_setting()
            
            # Assert
            assert os.path.exists(config_path)
        finally:
            shutil.rmtree(temp_dir)

    def test_create_default_setting_has_correct_values(self):
        # Arrange
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "config.ini")
        
        try:
            with mock.patch.object(Setting, 'CONFIG_FILE', config_path):
                setting = Setting()
                setting.create_default_setting()
            
            # Assert
            import configparser
            parser = configparser.ConfigParser()
            parser.read(config_path, encoding="utf-8")
            
            assert parser["GUI"]["Width"] == str(DEFAULT_WIDTH)
            assert parser["GUI"]["Height"] == str(DEFAULT_HEIGHT)
            assert parser["GUI"]["KeyPushedColor"] == str(DEFAULT_KEY_PUSHED_COLOR)
            assert parser["GUI"]["EnableMidiFile"] == str(DEFAULT_ENABLE_MIDI_FILE)
            assert parser["GUI"]["ImagePath"] == ""
            assert parser["GUI"]["ShowImageFrame"] == str(DEFAULT_SHOW_IMAGE_FRAME)
        finally:
            shutil.rmtree(temp_dir)
