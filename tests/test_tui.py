import pytest
import sys
from cedbox import Yggdrasil, TUI
from cedbox.tui import yggdrasil_to_tui

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
