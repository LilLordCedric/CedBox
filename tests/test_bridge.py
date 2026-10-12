import pytest
from unittest.mock import Mock, patch
from cedbox.yggdrasil import Yggdrasil
from cedbox.tui.bridge import (
    get_active_tui,
    set_active_tui,
    _interactive_input_action,
    yggdrasil_to_tui,
)
from cedbox.tui.nodes import Folder, Action, Switch


@pytest.fixture(autouse=True)
def reset_active_tui():
    """Ensure active TUI is reset before and after each test."""
    set_active_tui(None)
    yield
    set_active_tui(None)


def test_get_and_set_active_tui():
    assert get_active_tui() is None
    mock_tui = Mock()
    set_active_tui(mock_tui)
    assert get_active_tui() is mock_tui
    set_active_tui(None)
    assert get_active_tui() is None


def test_interactive_input_action_with_active_tui():
    mock_tui = Mock()
    set_active_tui(mock_tui)

    tree = {"volume": 50}
    input_func = Mock(return_value=75)

    action_fn = _interactive_input_action("volume", tree, input_func, str_default=False)
    result = action_fn()

    assert mock_tui.suspend.called
    assert mock_tui.resume.called
    input_func.assert_called_once_with("Enter new value for volume (current: 50): ", default=50)
    assert tree["volume"] == 75
    assert result == "volume set to 75"


def test_interactive_input_action_str_default():
    tree = {"name": "alice"}
    input_func = Mock(return_value="bob")

    action_fn = _interactive_input_action("name", tree, input_func, str_default=True)
    result = action_fn()

    input_func.assert_called_once_with("Enter new value for name (current: alice): ", default="alice")
    assert tree["name"] == "bob"
    assert result == "name set to bob"


def test_interactive_input_action_exception_handling():
    mock_tui = Mock()
    set_active_tui(mock_tui)

    tree = {"volume": 50}
    input_func = Mock(side_effect=ValueError("Invalid number"))

    action_fn = _interactive_input_action("volume", tree, input_func)
    result = action_fn()

    assert mock_tui.suspend.called
    # Ensure resume is called in finally block despite exception
    assert mock_tui.resume.called
    assert tree["volume"] == 50
    assert result == "Error setting volume: Invalid number"


def test_yggdrasil_to_tui_structure_and_types():
    tree = {
        "folder": {
            "sub_int": 42,
        },
        "my_func": lambda: "function executed",
        "my_bool": True,
        "my_int": 10,
        "my_float": 3.14,
        "my_str": "hello",
    }

    folder = yggdrasil_to_tui(tree, name="Root")
    assert isinstance(folder, Folder)
    assert folder.get_label() == "Root"

    children = {c.get_name(): c for c in folder.get_children()}
    assert "folder" in children
    assert "my_func" in children
    assert "my_bool" in children
    assert "my_int" in children
    assert "my_float" in children
    assert "my_str" in children

    # 1. Folder node
    sub_folder = children["folder"]
    assert isinstance(sub_folder, Folder)
    assert len(sub_folder.get_children()) == 1

    # 2. Callable -> Action
    func_node = children["my_func"]
    assert isinstance(func_node, Action)
    assert func_node.execute() == "function executed"

    # 3. Bool -> Switch
    bool_node = children["my_bool"]
    assert isinstance(bool_node, Switch)
    assert tree["my_bool"] is True
    assert bool_node.get_label() == "my_bool: [ON]"
    bool_node.execute()  # toggle
    assert tree["my_bool"] is False
    assert bool_node.get_label() == "my_bool: [OFF]"

    # 4. Int -> Action with label callback
    int_node = children["my_int"]
    assert isinstance(int_node, Action)
    assert int_node.get_label() == "my_int: 10"

    # 5. Float -> Action with label callback
    float_node = children["my_float"]
    assert isinstance(float_node, Action)
    assert float_node.get_label() == "my_float: 3.14"

    # 6. String -> Action with label callback
    str_node = children["my_str"]
    assert isinstance(str_node, Action)
    assert str_node.get_label() == "my_str: hello"


@patch("cedbox.tui.bridge.int_put", return_value=100)
@patch("cedbox.tui.bridge.float_put", return_value=2.718)
@patch("cedbox.tui.bridge.string_put", return_value="world")
def test_yggdrasil_to_tui_leaf_action_execution(mock_str_put, mock_float_put, mock_int_put):
    tree = {
        "val_int": 5,
        "val_float": 1.23,
        "val_str": "test",
    }

    folder = yggdrasil_to_tui(tree)
    children = {c.get_name(): c for c in folder.get_children()}

    res_int = children["val_int"].execute()
    mock_int_put.assert_called_once()
    assert tree["val_int"] == 100
    assert res_int == "val_int set to 100"

    res_float = children["val_float"].execute()
    mock_float_put.assert_called_once()
    assert tree["val_float"] == 2.718
    assert res_float == "val_float set to 2.718"

    res_str = children["val_str"].execute()
    mock_str_put.assert_called_once()
    assert tree["val_str"] == "world"
    assert res_str == "val_str set to world"
