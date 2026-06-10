from __future__ import annotations
from typing import Callable, List, Optional, Union, Any

class BaseNode:
    def __init__(self, label: Union[str, Callable[[], str]], hotkey: Optional[str] = None):
        self._label = label
        self.parent: Optional[BaseNode] = None
        self.active_check: Optional[Callable[[], bool]] = None
        self.hotkey = hotkey

    def set_active_check(self, callback: Callable[[], bool]):
        self.active_check = callback
        return self

    def is_active(self) -> bool:
        return self.active_check() if self.active_check else False

    def get_label(self) -> str:
        if callable(self._label):
            return self._label()
        return self._label

    def get_children(self) -> List[BaseNode]:
        return []

    def execute(self) -> Optional[str]:
        """Returns an optional message to display in the log."""
        return None

    def get_name(self) -> str:
        if hasattr(self, "name") and self.name is not None:
            return self.name
        if callable(self._label):
            return self._label()
        return self._label

    def get_path(self) -> str:
        parts = []
        curr = self
        while curr is not None:
            if curr.parent is not None:
                parts.append(curr.get_name())
            curr = curr.parent
        return "/".join(reversed(parts)) if parts else self.get_name()

    def to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "label": self.get_label(),
            "path": self.get_path()
        }

class Action(BaseNode):
    def __init__(self, label: str, callback: Callable[[], Optional[str]], hotkey: Optional[str] = None):
        super().__init__(label, hotkey=hotkey)
        self.callback = callback

    def execute(self) -> Optional[str]:
        return self.callback()

class Switch(BaseNode):
    def __init__(self, label: str, getter: Callable[[], bool], setter: Callable[[bool], None], hotkey: Optional[str] = None):
        super().__init__(label, hotkey=hotkey)
        self.getter = getter
        self.setter = setter

    def get_label(self) -> str:
        state = "[ON]" if self.getter() else "[OFF]"
        return f"{super().get_label()}: {state}"

    def execute(self) -> Optional[str]:
        new_state = not self.getter()
        self.setter(new_state)
        return f"{super().get_label()} set to {'ON' if new_state else 'OFF'}"

    def to_json(self) -> dict:
        data = super().to_json()
        data["value"] = self.getter()
        return data

class Checkbox(BaseNode):
    def __init__(self, label: str, getter: Callable[[], bool], setter: Callable[[bool], None]):
        super().__init__(label)
        self.getter = getter
        self.setter = setter

    def get_label(self) -> str:
        mark = "[X]" if self.getter() else "[ ]"
        return f"{mark} {super().get_label()}"

    def execute(self) -> Optional[str]:
        self.setter(not self.getter())
        return None

    def to_json(self) -> dict:
        data = super().to_json()
        data["value"] = self.getter()
        return data

class Slider(BaseNode):
    def __init__(self, label: str, min_v: float, max_v: float, step: float, 
                 getter: Callable[[], float], setter: Callable[[float], None]):
        super().__init__(label)
        self.min_v = min_v
        self.max_v = max_v
        self.step = step
        self.getter = getter
        self.setter = setter

    def get_label(self) -> str:
        val = self.getter()
        pct = int(((val - self.min_v) / (self.max_v - self.min_v)) * 10)
        bar = "█" * pct + "░" * (10 - pct)
        return f"{super().get_label()}: {bar} {val}%"

    def adjust(self, delta: float):
        new_val = max(self.min_v, min(self.max_v, self.getter() + delta))
        self.setter(new_val)

    def to_json(self) -> dict:
        data = super().to_json()
        data["value"] = self.getter()
        data["min"] = self.min_v
        data["max"] = self.max_v
        data["step"] = self.step
        return data

class Progress(BaseNode):
    def __init__(self, label: str, getter: Callable[[], float]):
        super().__init__(label)
        self.getter = getter

    def get_label(self) -> str:
        pct = min(100, max(0, self.getter()))
        bar_len = 10
        filled = int((pct / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        return f"{super().get_label()}: {bar} {pct}%"

class InputNode(BaseNode):
    def __init__(self, label: str, callback: Callable[[str], Optional[str]]):
        super().__init__(label)
        self.callback = callback

    def execute_input(self, text: str) -> Optional[str]:
        return self.callback(text)

class EditorNode(BaseNode):
    def __init__(self, label: str, getter: Callable[[], str], setter: Callable[[str], Optional[str]]):
        super().__init__(label)
        self.getter = getter
        self.setter = setter

    def get_content(self) -> str:
        return self.getter()

    def save_content(self, text: str) -> Optional[str]:
        return self.setter(text)

class Folder(BaseNode):
    def __init__(self, label: Union[str, Callable[[], str]], children: List[BaseNode], hotkey: Optional[str] = None):
        super().__init__(label, hotkey=hotkey)
        self.children = children
        for child in self.children:
            child.parent = self

    def get_children(self) -> List[BaseNode]:
        return self.children

    def to_json(self) -> dict:
        data = super().to_json()
        data["children"] = [c.to_json() for c in self.children]
        return data

class DynamicSelect(BaseNode):
    """A node that generates its children dynamically (e.g. file lists)."""
    def __init__(self, label: Union[str, Callable[[], str]], generator: Callable[[], List[Union[str, BaseNode]]], 
                 on_select: Optional[Callable[[str], Optional[str]]] = None,
                 active_item_check: Optional[Callable[[str], bool]] = None,
                 hotkey: Optional[str] = None):
        super().__init__(label, hotkey=hotkey)
        self.generator = generator
        self.on_select = on_select
        self.active_item_check = active_item_check

    def get_children(self) -> List[BaseNode]:
        items = self.generator()
        nodes = []
        for item in items:
            if isinstance(item, BaseNode):
                item.parent = self
                nodes.append(item)
            else:
                # Wrap string as an action
                node = Action(str(item), lambda val=item: self.on_select(val) if self.on_select else None)
                node.parent = self
                if self.active_item_check:
                    node.set_active_check(lambda val=item: self.active_item_check(val))
                nodes.append(node)
        return nodes

    def to_json(self) -> dict:
        data = super().to_json()
        data["children"] = [c.to_json() for c in self.get_children()]
        return data
