import pytest
from unittest.mock import Mock, call

from cedbox.tui.nodes import (
    BaseNode, Action, Switch, Checkbox, Slider, Progress,
    InputNode, EditorNode, Folder, DynamicSelect
)

def test_basenode_label_string():
    node = BaseNode("My Label", hotkey="x")
    assert node.get_label() == "My Label"
    assert node.get_name() == "My Label"
    assert node.hotkey == "x"
    assert node.get_children() == []
    assert node.execute() is None

def test_basenode_label_callable():
    node = BaseNode(lambda: "Dynamic Label")
    assert node.get_label() == "Dynamic Label"
    assert node.get_name() == "Dynamic Label"

def test_basenode_active_check():
    node = BaseNode("Label")
    assert not node.is_active()

    mock_check = Mock(return_value=True)
    assert node.set_active_check(mock_check) == node
    assert node.is_active()
    mock_check.assert_called_once()

def test_basenode_path_and_json():
    root = BaseNode("Root")
    child = BaseNode("Child")
    subchild = BaseNode("Subchild")

    child.parent = root
    subchild.parent = child

    # get_path excludes the root node (node with no parent) when returning paths for children
    assert root.get_path() == "Root"
    assert child.get_path() == "Child"
    assert subchild.get_path() == "Child/Subchild"

    json_data = subchild.to_json()
    assert json_data == {
        "type": "BaseNode",
        "label": "Subchild",
        "path": "Child/Subchild"
    }

def test_action():
    mock_callback = Mock(return_value="Action executed")
    action = Action("Run Task", mock_callback, hotkey="r")

    assert action.get_label() == "Run Task"
    assert action.hotkey == "r"
    assert action.execute() == "Action executed"
    mock_callback.assert_called_once()

def test_switch():
    state = {"value": False}
    def getter(): return state["value"]
    def setter(val): state["value"] = val

    switch = Switch("Enable Feature", getter, setter, hotkey="e")

    assert switch.get_label() == "Enable Feature: [OFF]"

    res = switch.execute()
    assert state["value"] is True
    assert res == "Enable Feature set to ON"
    assert switch.get_label() == "Enable Feature: [ON]"

    json_data = switch.to_json()
    assert json_data["type"] == "Switch"
    assert json_data["value"] is True

def test_checkbox():
    state = {"value": True}
    def getter(): return state["value"]
    def setter(val): state["value"] = val

    checkbox = Checkbox("Option A", getter, setter)

    assert checkbox.get_label() == "[X] Option A"

    res = checkbox.execute()
    assert res is None
    assert state["value"] is False
    assert checkbox.get_label() == "[ ] Option A"

    json_data = checkbox.to_json()
    assert json_data["type"] == "Checkbox"
    assert json_data["value"] is False

def test_slider():
    state = {"value": 50.0}
    def getter(): return state["value"]
    def setter(val): state["value"] = val

    slider = Slider("Volume", 0.0, 100.0, 10.0, getter, setter)

    assert slider.get_label() == "Volume: █████░░░░░ 50.0%"

    slider.adjust(20.0)
    assert state["value"] == 70.0

    slider.adjust(50.0) # Should clamp to max
    assert state["value"] == 100.0

    slider.adjust(-150.0) # Should clamp to min
    assert state["value"] == 0.0

    json_data = slider.to_json()
    assert json_data["type"] == "Slider"
    assert json_data["value"] == 0.0
    assert json_data["min"] == 0.0
    assert json_data["max"] == 100.0
    assert json_data["step"] == 10.0

def test_progress():
    state = {"value": 75.0}
    progress = Progress("Download", lambda: state["value"])

    assert progress.get_label() == "Download: ███████░░░ 75.0%"

    state["value"] = 150.0
    assert progress.get_label() == "Download: ██████████ 100%"

    state["value"] = -10.0
    assert progress.get_label() == "Download: ░░░░░░░░░░ 0%"

def test_input_node():
    mock_callback = Mock(return_value="Input received")
    node = InputNode("Enter Name", mock_callback)

    assert node.get_label() == "Enter Name"
    assert node.execute_input("Alice") == "Input received"
    mock_callback.assert_called_once_with("Alice")

def test_editor_node():
    state = {"content": "Initial text"}
    def getter(): return state["content"]
    def setter(val):
        state["content"] = val
        return "Saved"

    editor = EditorNode("Config", getter, setter)

    assert editor.get_content() == "Initial text"
    assert editor.save_content("New text") == "Saved"
    assert state["content"] == "New text"

def test_folder():
    child1 = BaseNode("Child1")
    child2 = BaseNode("Child2")
    folder = Folder("My Folder", [child1, child2], hotkey="f")

    assert folder.get_label() == "My Folder"
    assert folder.hotkey == "f"
    assert folder.get_children() == [child1, child2]
    assert child1.parent == folder
    assert child2.parent == folder

    json_data = folder.to_json()
    assert json_data["type"] == "Folder"
    assert len(json_data["children"]) == 2
    assert json_data["children"][0]["label"] == "Child1"
    assert json_data["children"][1]["label"] == "Child2"

def test_dynamic_select_with_nodes():
    item1 = BaseNode("Item1")
    item2 = BaseNode("Item2")

    def generator(): return [item1, item2]

    node = DynamicSelect("DynSelect", generator)

    children = node.get_children()
    assert len(children) == 2
    assert children[0] == item1
    assert children[1] == item2
    assert item1.parent == node
    assert item2.parent == node

    json_data = node.to_json()
    assert json_data["type"] == "DynamicSelect"
    assert len(json_data["children"]) == 2

def test_dynamic_select_with_strings():
    def generator(): return ["Apple", "Banana"]

    mock_on_select = Mock(return_value="Selected")
    mock_active_check = Mock(side_effect=lambda x: x == "Apple")

    node = DynamicSelect("Fruits", generator, on_select=mock_on_select, active_item_check=mock_active_check)

    children = node.get_children()
    assert len(children) == 2

    assert isinstance(children[0], Action)
    assert children[0].get_label() == "Apple"
    assert children[0].parent == node
    assert children[0].is_active() is True

    assert isinstance(children[1], Action)
    assert children[1].get_label() == "Banana"
    assert children[1].parent == node
    assert children[1].is_active() is False

    res = children[1].execute()
    assert res == "Selected"
    mock_on_select.assert_called_once_with("Banana")
