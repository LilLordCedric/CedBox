from typing import Optional, Union, Dict, Any, Callable
from cedbox.yggdrasil import Yggdrasil
from cedbox.tui.nodes import BaseNode, Folder, Action, Switch, Slider, InputNode, Checkbox
from cedbox.inputs import string_put, int_put, float_put, bool_put

# We keep a reference to the active TUI instance globally or thread-locally
_active_tui: Optional[Any] = None

def get_active_tui() -> Optional[Any]:
    return _active_tui

def set_active_tui(tui_instance: Any):
    global _active_tui
    _active_tui = tui_instance

def yggdrasil_to_tui(tree: Union[Yggdrasil, dict], name: str = "Root") -> Folder:
    """
    Recursively maps an Yggdrasil (or dict) tree structure to a TUI Folder/Node hierarchy.
    Leaf values are converted to interactive TUI settings/actions.
    """
    children = []
    for key, value in tree.items():
        if isinstance(value, (Yggdrasil, dict)):
            # Recurse for folders
            folder = yggdrasil_to_tui(value, name=key)
            folder.name = key
            children.append(folder)
        elif callable(value):
            # A direct callable maps to an Action
            node = Action(key, value)
            node.name = key
            children.append(node)
        elif isinstance(value, bool):
            # Boolean maps to a Switch (ON/OFF)
            def make_getter(k=key, t=tree):
                return lambda: t[k]
            def make_setter(k=key, t=tree):
                return lambda v: t.__setitem__(k, v)
            node = Switch(key, getter=make_getter(), setter=make_setter())
            node.name = key
            children.append(node)
        elif isinstance(value, (int, float)):
            # If it's a number, we can use an Action that suspends the TUI
            # and runs the console input validation functions (int_put / float_put) from cedbox.inputs!
            def make_action(k=key, t=tree, is_float=isinstance(value, float)):
                def run_input():
                    tui = get_active_tui()
                    if tui:
                        tui.suspend()
                    try:
                        prompt = f"Enter new value for {k} (current: {t[k]}): "
                        if is_float:
                            new_val = float_put(prompt, default=t[k])
                        else:
                            new_val = int_put(prompt, default=t[k])
                        t[k] = new_val
                        return f"{k} set to {new_val}"
                    except Exception as e:
                        return f"Error setting {k}: {e}"
                    finally:
                        if tui:
                            tui.resume()
                return run_input
            
            # We display the current value in the Action label dynamically
            def make_label(k=key, t=tree):
                return lambda: f"{k}: {t[k]}"
            
            node = Action(make_label(), make_action())
            node.name = key
            children.append(node)
        else:
            # Any other leaf type (usually string) maps to string_put input function
            def make_action(k=key, t=tree):
                def run_input():
                    tui = get_active_tui()
                    if tui:
                        tui.suspend()
                    try:
                        prompt = f"Enter new value for {k} (current: {t[k]}): "
                        new_val = string_put(prompt, default=str(t[k]))
                        t[k] = new_val
                        return f"{k} set to {new_val}"
                    except Exception as e:
                        return f"Error setting {k}: {e}"
                    finally:
                        if tui:
                            tui.resume()
                return run_input
            
            def make_label(k=key, t=tree):
                return lambda: f"{k}: {t[k]}"
            
            node = Action(make_label(), make_action())
            node.name = key
            children.append(node)
            
    root_folder = Folder(name, children)
    root_folder.name = name
    return root_folder
