import pytest
import sys
from unittest.mock import patch
from cedbox import Yggdrasil, TUI
from cedbox.tui import yggdrasil_to_tui
from cedbox.tui.core import color_text

class TestTUIYggdrasil:
    def test_yggdrasil_to_tui_basic(self):
        """Test basic translation from Yggdrasil to TUI nodes"""
        tree = Yggdrasil()
        tree["Settings"]["System"]["Volume"] = 50
        tree["Settings"]["System"]["Muted"] = True
        tree["Actions"]["SayHello"] = lambda: "Hello"
        
        folder = yggdrasil_to_tui(tree, "TestRoot")
        assert folder.get_label() == "TestRoot"
        
        children = folder.get_children()
        assert len(children) == 2
        labels = [c.get_label() for c in children]
        assert "Settings" in labels
        assert "Actions" in labels

    def test_tui_builders_and_decorators(self):
        """Test adding settings, switches, and actions to TUI using builders & decorators"""
        tui = TUI(title="BuilderApp")
        tui.add_switch("Muted", default=True, parent="Settings/System")
        tui.add_setting("Volume", default=85, parent="Settings/System")
        
        @tui.action("Quit", "Actions")
        def quit_app():
            return "Quit Triggered"

        @tui.action(abs="Actions/Greet")
        def greet():
            return "Greet Triggered"
            
        # Manually trigger root building logic
        tui.root = yggdrasil_to_tui(tui.state, tui.title)
        
        # Verify schema export
        schema = tui.to_json()
        assert schema["title"] == "BuilderApp"
        assert len(schema["menu"]["children"]) == 2 # Settings & Actions
        
        # Verify execution via path
        res_mute = tui.execute_json_path("Settings/System/Muted")
        assert res_mute["status"] == "success"
        # Since Muted was True, toggling it makes it False
        assert tui.state["Settings"]["System"]["Muted"] is False
        
        # Verify updating setting value
        res_vol = tui.execute_json_path("Settings/System/Volume", 60)
        assert res_vol["status"] == "success"
        assert tui.state["Settings"]["System"]["Volume"] == 60

    @patch("sys.stdout")
    def test_tui_suspend(self, mock_stdout):
        """Test TUI suspend writes correct ANSI escape sequences"""
        tui = TUI(title="SuspendApp")
        tui.suspend()
        mock_stdout.write.assert_called_with("\033[?1000l\033[?25h\033[?1049l")
        mock_stdout.flush.assert_called_once()

    @patch("sys.stdout")
    def test_tui_resume(self, mock_stdout):
        """Test TUI resume writes correct ANSI escape sequences"""
        tui = TUI(title="ResumeApp")
        tui.resume()
        mock_stdout.write.assert_called_with("\033[?1049h\033[?1000h\033[?25l\033[H\033[J")
        mock_stdout.flush.assert_called_once()
def test_color_text():
    """Test the color_text utility function."""
    assert color_text("Hello", "31") == "\033[31mHello\033[0m"
    assert color_text("World", "32") == "\033[32mWorld\033[0m"
    assert color_text("", "0") == "\033[0m\033[0m"
    assert color_text("Test", "1;31") == "\033[1;31mTest\033[0m"
