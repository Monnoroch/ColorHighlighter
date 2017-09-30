"""Tests for settings module."""

import unittest

from ColorHighlighter import st_helper  # pylint: disable=no-name-in-module
from ColorHighlighter.settings import (  # pylint: disable=no-name-in-module,import-error
    ColorSchemeColorHighlighterSettings, GutterIconsColorHighlighterSettings)
from ColorHighlighter.settings import Settings  # pylint: disable=no-name-in-module,import-error

from mockito import unstub, when


class SettingsTest(unittest.TestCase):
    """Tests for Settings."""

    def test_create(self):
        """Test creating color format settings."""
        settings = Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "text"
                        },
                        "gutter_icons": {
                            "enabled": True,
                            "icon_style": "square"
                        },
                        "phantoms": {
                            "enabled": True
                        }
                    }
                },
                "all_content": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "text"
                        },
                        "gutter_icons": {
                            "enabled": True,
                            "icon_style": "square"
                        },
                        "phantoms": {
                            "enabled": True
                        }
                    }
                },
                "hover": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "text"
                        },
                        "gutter_icons": {
                            "enabled": True,
                            "icon_style": "square"
                        },
                        "phantoms": {
                            "enabled": True
                        }
                    }
                }
            },
            "default_keybindings": False,
            "file_extensions": [".py", ".css"],
            "icon_factory": {
                "convert_command": "test-convert",
                "convert_timeout": 10
            },
            "autoreload": {
                "when_settings_change": True,
                "when_color_scheme_change": True
            },
            "regex_compiler": {
                "channels": {
                    "hex": "[0-9a-fA-F]",
                },
                "formats": {
                    "sharp8": {
                        "description": "test description",
                        "regex": "#[0-9a-fA-F]{8}",
                        "white": "#FFFFFFFF",
                        "after": ["test-after"]
                    },
                }
            },
            "experimental": {
                "asynchronosly_update_color_scheme": True,
            },
            "debug": True,
        })
        self.assertEqual(
            {"selection": True, "all_content": True, "hover": True},
            settings.search_colors_in.color_searcher_names)

        self.assertEqual(True, settings.search_colors_in.selection.enabled)
        self.assertEqual("selection", settings.search_colors_in.selection.name)
        self.assertEqual(
            {"color_scheme": True, "gutter_icons": True, "phantoms": True},
            settings.search_colors_in.selection.color_highlighters.color_highlighter_names)
        self.assertEqual(True, settings.search_colors_in.selection.color_highlighters.color_scheme.enabled)
        self.assertEqual(
            "text", settings.search_colors_in.selection.color_highlighters.color_scheme.highlight_style)
        self.assertEqual(True, settings.search_colors_in.selection.color_highlighters.gutter_icons.enabled)
        self.assertEqual("square", settings.search_colors_in.selection.color_highlighters.gutter_icons.icon_style)
        self.assertEqual(True, settings.search_colors_in.selection.color_highlighters.phantoms.enabled)

        self.assertEqual(True, settings.search_colors_in.all_content.enabled)
        self.assertEqual("all_content", settings.search_colors_in.all_content.name)
        self.assertEqual(
            {"color_scheme": True, "gutter_icons": True, "phantoms": True},
            settings.search_colors_in.all_content.color_highlighters.color_highlighter_names)
        self.assertEqual(True, settings.search_colors_in.all_content.color_highlighters.color_scheme.enabled)
        self.assertEqual(
            "text", settings.search_colors_in.all_content.color_highlighters.color_scheme.highlight_style)
        self.assertEqual(True, settings.search_colors_in.all_content.color_highlighters.gutter_icons.enabled)
        self.assertEqual(
            "square", settings.search_colors_in.all_content.color_highlighters.gutter_icons.icon_style)
        self.assertEqual(True, settings.search_colors_in.all_content.color_highlighters.phantoms.enabled)

        self.assertEqual(True, settings.search_colors_in.hover.enabled)
        self.assertEqual("hover", settings.search_colors_in.hover.name)
        self.assertEqual(
            {"color_scheme": True, "gutter_icons": True, "phantoms": True},
            settings.search_colors_in.hover.color_highlighters.color_highlighter_names)
        self.assertEqual(True, settings.search_colors_in.hover.color_highlighters.color_scheme.enabled)
        self.assertEqual(
            "text", settings.search_colors_in.hover.color_highlighters.color_scheme.highlight_style)
        self.assertEqual(True, settings.search_colors_in.hover.color_highlighters.gutter_icons.enabled)
        self.assertEqual(
            "square", settings.search_colors_in.hover.color_highlighters.gutter_icons.icon_style)
        self.assertEqual(True, settings.search_colors_in.hover.color_highlighters.phantoms.enabled)

        self.assertEqual(False, settings.default_keybindings)
        self.assertEqual({".py": True, ".css": True}, settings.file_extensions)

        self.assertEqual("test-convert", settings.icon_factory.convert_command)
        self.assertEqual(10, settings.icon_factory.convert_timeout)

        self.assertEqual(True, settings.autoreload.when_settings_change)
        self.assertEqual(True, settings.autoreload.when_color_scheme_change)

        self.assertEqual({"hex": "[0-9a-fA-F]"}, settings.regex_compiler.channels)
        self.assertEqual(["sharp8"], [name for name in settings.regex_compiler.formats])
        self.assertEqual("test description", settings.regex_compiler.formats["sharp8"].description)
        self.assertEqual("#[0-9a-fA-F]{8}", settings.regex_compiler.formats["sharp8"].regex)
        self.assertEqual("#FFFFFFFF", settings.regex_compiler.formats["sharp8"].white)
        self.assertEqual(["test-after"], settings.regex_compiler.formats["sharp8"].after)

        self.assertEqual(True, settings.experimental.asynchronosly_update_color_scheme)
        self.assertTrue(settings.debug)

    def test_create_default(self):
        """Test creating color format settings with default values."""
        settings = Settings({
            "regex_compiler": {
                "formats": {
                    "sharp8": {
                        "description": "test description",
                        "regex": "#[0-9a-fA-F]{8}",
                        "white": "#FFFFFFFF",
                    },
                }
            }
        })
        self.assertEqual(
            {"selection": True, "all_content": True, "hover": True},
            settings.search_colors_in.color_searcher_names)

        self.assertEqual(False, settings.search_colors_in.selection.enabled)
        self.assertEqual("selection", settings.search_colors_in.selection.name)
        self.assertEqual(
            {"color_scheme": True, "gutter_icons": True, "phantoms": True},
            settings.search_colors_in.selection.color_highlighters.color_highlighter_names)
        self.assertEqual(False, settings.search_colors_in.selection.color_highlighters.color_scheme.enabled)
        self.assertEqual(
            "filled", settings.search_colors_in.selection.color_highlighters.color_scheme.highlight_style)
        self.assertEqual(False, settings.search_colors_in.selection.color_highlighters.gutter_icons.enabled)
        self.assertEqual("circle", settings.search_colors_in.selection.color_highlighters.gutter_icons.icon_style)
        self.assertEqual(False, settings.search_colors_in.selection.color_highlighters.phantoms.enabled)

        self.assertEqual(False, settings.search_colors_in.all_content.enabled)
        self.assertEqual("all_content", settings.search_colors_in.all_content.name)
        self.assertEqual(
            {"color_scheme": True, "gutter_icons": True, "phantoms": True},
            settings.search_colors_in.all_content.color_highlighters.color_highlighter_names)
        self.assertEqual(False, settings.search_colors_in.all_content.color_highlighters.color_scheme.enabled)
        self.assertEqual(
            "filled", settings.search_colors_in.all_content.color_highlighters.color_scheme.highlight_style)
        self.assertEqual(False, settings.search_colors_in.all_content.color_highlighters.gutter_icons.enabled)
        self.assertEqual(
            "circle", settings.search_colors_in.all_content.color_highlighters.gutter_icons.icon_style)
        self.assertEqual(False, settings.search_colors_in.all_content.color_highlighters.phantoms.enabled)

        self.assertEqual(False, settings.search_colors_in.hover.enabled)
        self.assertEqual("hover", settings.search_colors_in.hover.name)
        self.assertEqual(
            {"color_scheme": True, "gutter_icons": True, "phantoms": True},
            settings.search_colors_in.hover.color_highlighters.color_highlighter_names)
        self.assertEqual(False, settings.search_colors_in.hover.color_highlighters.color_scheme.enabled)
        self.assertEqual(
            "filled", settings.search_colors_in.hover.color_highlighters.color_scheme.highlight_style)
        self.assertEqual(False, settings.search_colors_in.hover.color_highlighters.gutter_icons.enabled)
        self.assertEqual(
            "circle", settings.search_colors_in.hover.color_highlighters.gutter_icons.icon_style)
        self.assertEqual(False, settings.search_colors_in.hover.color_highlighters.phantoms.enabled)

        self.assertEqual(True, settings.default_keybindings)
        self.assertEqual({}, settings.file_extensions)

        self.assertEqual("convert", settings.icon_factory.convert_command)
        self.assertEqual(5, settings.icon_factory.convert_timeout)

        self.assertEqual(False, settings.autoreload.when_settings_change)
        self.assertEqual(False, settings.autoreload.when_color_scheme_change)

        self.assertEqual({}, settings.regex_compiler.channels)
        self.assertEqual(["sharp8"], [name for name in settings.regex_compiler.formats])
        self.assertEqual("test description", settings.regex_compiler.formats["sharp8"].description)
        self.assertEqual("#[0-9a-fA-F]{8}", settings.regex_compiler.formats["sharp8"].regex)
        self.assertEqual("#FFFFFFFF", settings.regex_compiler.formats["sharp8"].white)
        self.assertEqual([], settings.regex_compiler.formats["sharp8"].after)

        self.assertEqual(False, settings.experimental.asynchronosly_update_color_scheme)
        self.assertFalse(settings.debug)

    def test_create_single_after(self):
        """Test creating color format settings with singular format after field."""
        settings = Settings({
            "regex_compiler": {
                "formats": {
                    "sharp8": {
                        "description": "test description",
                        "regex": "#[0-9a-fA-F]{8}",
                        "white": "#FFFFFFFF",
                        "after": "test-after"
                    },
                }
            }
        })
        self.assertEqual(["test-after"], settings.regex_compiler.formats["sharp8"].after)

    def test_create_no_format_description(self):  # pylint: disable=invalid-name
        """Test creating color format settings with format that doesn't have a descrption."""
        self.assertRaises(KeyError, lambda: Settings({
            "regex_compiler": {
                "formats": {
                    "sharp8": {
                        "regex": "#[0-9a-fA-F]{8}",
                        "white": "#FFFFFFFF",
                    },
                }
            }
        }))

    def test_create_no_format_regex(self):
        """Test creating color format settings with format that doesn't have a regex."""
        self.assertRaises(KeyError, lambda: Settings({
            "regex_compiler": {
                "formats": {
                    "sharp8": {
                        "description": "test description",
                        "white": "#FFFFFFFF",
                    },
                }
            }
        }))

    def test_create_no_format_white(self):
        """Test creating color format settings with format that doesn't have a white example."""
        self.assertRaises(KeyError, lambda: Settings({
            "regex_compiler": {
                "formats": {
                    "sharp8": {
                        "description": "test description",
                        "regex": "#[0-9a-fA-F]{8}",
                    },
                }
            }
        }))

    def test_create_invalid_highlight_style(self):  # pylint: disable=invalid-name
        """Test creating color highlighting settings with invaid highlighting style."""
        self.assertRaises(AssertionError, lambda: Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "invalid-style"
                        },
                    }
                }
            }
        }))

    def test_create_invalid_icon_style(self):
        """Test creating color highlighting settings with invaid icon style."""
        self.assertRaises(AssertionError, lambda: Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "gutter_icons": {
                            "enabled": True,
                            "icon_style": "invalid-style"
                        },
                    }
                }
            }
        }))

    def test_create_underline_solid_highlight_style_invalid_st2(self):  # pylint: disable=invalid-name
        """
        Test creating color highlighting settings with invaid highlighting style.

        underline_solid highlighting style is invalid in ST2.
        """
        when(st_helper).is_st3().thenReturn(False)
        self.assertRaises(AssertionError, lambda: Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "underline_solid"
                        },
                    }
                }
            }
        }))
        unstub(st_helper)

    def test_create_underlined_strippled_highlight_style_invalid_st2(self):  # pylint: disable=invalid-name
        """
        Test creating color highlighting settings with invaid highlighting style.

        underlined_strippled highlighting style is invalid in ST2.
        """
        when(st_helper).is_st3().thenReturn(False)
        self.assertRaises(AssertionError, lambda: Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "underlined_strippled"
                        },
                    }
                }
            }
        }))
        unstub(st_helper)

    def test_create_underlined_squiggly_highlight_style_invalid_st2(self):  # pylint: disable=invalid-name
        """
        Test creating color highlighting settings with invaid highlighting style.

        underlined_squiggly highlighting style is invalid in ST2.
        """
        when(st_helper).is_st3().thenReturn(False)
        self.assertRaises(AssertionError, lambda: Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "color_scheme": {
                            "enabled": True,
                            "highlight_style": "underlined_squiggly"
                        },
                    }
                }
            }
        }))
        unstub(st_helper)

    def test_create_enable_gutter_icons_st2(self):  # pylint: disable=invalid-name
        """Test gutter icons can't be enabled in ST2."""
        when(st_helper).is_st3().thenReturn(False)
        settings = Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "gutter_icons": {
                            "enabled": True,
                        },
                    }
                }
            }
        })
        self.assertFalse(settings.search_colors_in.selection.color_highlighters.gutter_icons.enabled)
        unstub(st_helper)

    def test_asynchronosly_update_color_scheme_st2(self):  # pylint: disable=invalid-name
        """Test asynchronosly updating color scheme can't be enabled in ST2."""
        when(st_helper).is_st3().thenReturn(False)
        settings = Settings({
            "experimental": {
                "asynchronosly_update_color_scheme": True
            }
        })
        self.assertFalse(settings.experimental.asynchronosly_update_color_scheme)
        unstub(st_helper)

    def test_create_enable_phantoms_st2(self):
        """Test phantoms can't be enabled in ST2."""
        when(st_helper).is_st3().thenReturn(False)
        settings = Settings({
            "search_colors_in": {
                "selection": {
                    "enabled": True,
                    "color_highlighters": {
                        "phantoms": {
                            "enabled": True,
                        },
                    }
                }
            }
        })
        self.assertFalse(settings.search_colors_in.selection.color_highlighters.phantoms.enabled)
        unstub(st_helper)

    def test_create_enable_hover(self):
        """Test phantoms can't be enabled in ST2."""
        when(st_helper).is_st3().thenReturn(False)
        settings = Settings({
            "search_colors_in": {
                "hover": {
                    "enabled": True,
                }
            }
        })
        self.assertFalse(settings.search_colors_in.hover.color_highlighters.phantoms.enabled)
        unstub(st_helper)


class ColorSchemeColorHighlighterSettingsTest(unittest.TestCase):
    """Tests for ColorSchemeColorHighlighterSettings."""

    def test_create(self):
        """Test creating color format settings."""
        settings = ColorSchemeColorHighlighterSettings({
            "enabled": True,
            "highlight_style": "text"
        })
        self.assertTrue(settings.enabled)
        self.assertEqual("text", settings.highlight_style)

    def test_create_default(self):
        """Test creating color format settings with default values."""
        settings = ColorSchemeColorHighlighterSettings({})
        self.assertFalse(settings.enabled)
        self.assertEqual("filled", settings.highlight_style)

    def test_create_invalid_highlight_style(self):  # pylint: disable=invalid-name
        """Test creating color highlighting settings with invaid highlighting style."""
        self.assertRaises(AssertionError, lambda: ColorSchemeColorHighlighterSettings({
            "enabled": True,
            "highlight_style": "invalid-style"
        }))

    def test_create_underline_solid_highlight_style_invalid_st2(self):  # pylint: disable=invalid-name
        """
        Test creating color highlighting settings with invaid highlighting style.

        underline_solid highlighting style is invalid in ST2.
        """
        when(st_helper).is_st3().thenReturn(False)
        self.assertRaises(AssertionError, lambda: ColorSchemeColorHighlighterSettings({
            "enabled": True,
            "highlight_style": "underline_solid"
        }))
        unstub(st_helper)

    def test_create_underlined_strippled_highlight_style_invalid_st2(self):  # pylint: disable=invalid-name
        """
        Test creating color highlighting settings with invaid highlighting style.

        underlined_strippled highlighting style is invalid in ST2.
        """
        when(st_helper).is_st3().thenReturn(False)
        self.assertRaises(AssertionError, lambda: ColorSchemeColorHighlighterSettings({
            "enabled": True,
            "highlight_style": "underlined_strippled"
        }))
        unstub(st_helper)

    def test_create_underlined_squiggly_highlight_style_invalid_st2(self):  # pylint: disable=invalid-name
        """
        Test creating color highlighting settings with invaid highlighting style.

        underlined_squiggly highlighting style is invalid in ST2.
        """
        when(st_helper).is_st3().thenReturn(False)
        self.assertRaises(AssertionError, lambda: ColorSchemeColorHighlighterSettings({
            "enabled": True,
            "highlight_style": "underlined_squiggly"
        }))
        unstub(st_helper)


class GutterIconsColorHighlighterSettingsTest(unittest.TestCase):
    """Tests for GutterIconsColorHighlighterSettings."""

    def test_create(self):
        """Test creating color format settings."""
        settings = GutterIconsColorHighlighterSettings({
            "enabled": True,
            "icon_style": "square"
        })
        self.assertTrue(settings.enabled)
        self.assertEqual("square", settings.icon_style)

    def test_create_default(self):
        """Test creating color format settings with default values."""
        settings = GutterIconsColorHighlighterSettings({})
        self.assertFalse(settings.enabled)
        self.assertEqual("circle", settings.icon_style)

    def test_create_invalid_icon_style(self):
        """Test creating color highlighting settings with invaid icon style."""
        self.assertRaises(AssertionError, lambda: GutterIconsColorHighlighterSettings({
            "enabled": True,
            "icon_style": "invalid-style"
        }))

    def test_create_enable_gutter_icons_st2(self):  # pylint: disable=invalid-name
        """Test gutter icons can't be enabled in ST2."""
        when(st_helper).is_st3().thenReturn(False)
        settings = GutterIconsColorHighlighterSettings({
            "enabled": True,
        })
        self.assertFalse(settings.enabled)
        unstub(st_helper)
