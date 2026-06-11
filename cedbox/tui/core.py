import os
import sys
import tty
import termios
import select
import time
import threading
from typing import List, Optional, Callable, Dict, Union, Any
from .nodes import BaseNode, Folder

def color_text(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"

class TUI:
    def __init__(self, root_node: Optional[Union[Folder, 'Yggdrasil', dict]] = None, title: str = "CEDTUI", min_height: int = 1, max_height: Optional[int] = None):
        from .bridge import yggdrasil_to_tui
        from ..yggdrasil import Yggdrasil
        from .nodes import BaseNode
        
        self.title = title
        
        # Initialize background state
        if isinstance(root_node, Yggdrasil):
            self.state = root_node
            self.root = None
        elif isinstance(root_node, dict) and not isinstance(root_node, BaseNode):
            self.state = Yggdrasil()
            for k, v in root_node.items():
                self.state[k] = v
            self.root = None
        elif isinstance(root_node, BaseNode):
            self.root = root_node
            self.state = Yggdrasil()
        else:
            self.state = Yggdrasil()
            self.root = None
            
        if self.root:
            self.columns: List[List[BaseNode]] = [self.root.get_children()]
            self.indices: List[int] = [0]
            self.scroll_offsets: List[int] = [0]
        else:
            self.columns = []
            self.indices = []
            self.scroll_offsets = []
            
        self.active_col = 0
        self.message = ""
        self.running = True
        self.status_callback: Optional[Callable[[], List[str]]] = None
        
        # New features
        self.search_mode = False
        self.search_buffer = ""
        self.edit_mode = False  # For Slider/Input
        self.editor_mode = False # For multi-line EditorNode
        self.editor_buffer: List[str] = []
        self.editor_cursor = [0, 0] # row, col
        self.show_help = False
        
        # Sizing
        self.min_height = min_height
        self.max_height = max_height

    def set_status_callback(self, callback: Callable[[], List[str]]):
        self.status_callback = callback

    def add_switch(self, path: Optional[str] = None, default: bool = False, parent: Optional[str] = None, abs: Optional[str] = None):
        full_path = abs if abs is not None else (f"{parent}/{path}" if parent else path)
        if not full_path:
            raise ValueError("Either path or abs must be provided")
        self.state.add_fiber(full_path.split("/") + [default])
        return self

    def add_setting(self, path: Optional[str] = None, default: Any = None, parent: Optional[str] = None, abs: Optional[str] = None):
        full_path = abs if abs is not None else (f"{parent}/{path}" if parent else path)
        if not full_path:
            raise ValueError("Either path or abs must be provided")
        self.state.add_fiber(full_path.split("/") + [default])
        return self

    def add_action(self, path: Optional[str] = None, callback: Optional[Callable] = None, parent: Optional[str] = None, abs: Optional[str] = None):
        full_path = abs if abs is not None else (f"{parent}/{path}" if parent else path)
        if not full_path:
            raise ValueError("Either path or abs must be provided")
        self.state.add_fiber(full_path.split("/") + [callback])
        return self

    def action(self, path: Optional[str] = None, parent: Optional[str] = None, abs: Optional[str] = None):
        def decorator(func):
            self.add_action(path, func, parent=parent, abs=abs)
            return func
        return decorator

    def _get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                data = os.read(fd, 6)
                if data:
                    if len(data) == 6 and data.startswith(b'\x1b[M'):
                        cb = data[3]
                        if cb == 33: # Middle click press
                            return '\x1b[C' # Right
                        elif cb == 96: # Mouse wheel up
                            return '\x1b[A' # Up
                        elif cb == 97: # Mouse wheel down
                            return '\x1b[B' # Down
                        return None
                    return data.decode('utf-8', errors='ignore')
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_filtered_column(self, col_idx: int) -> List[BaseNode]:
        nodes = self.columns[col_idx]
        if col_idx == self.active_col and self.search_buffer and not self.edit_mode:
            return [n for n in nodes if self.search_buffer.lower() in n.get_label().lower()]
        return nodes

    def get_breadcrumbs(self) -> str:
        parts = []
        for i in range(self.active_col):
            parent_idx = self.indices[i]
            parent_nodes = self.get_filtered_column(i)
            if parent_idx < len(parent_nodes):
                parts.append(parent_nodes[parent_idx].get_label())
        return " > ".join(parts) if parts else "Root"

    def draw(self):
        term_width, term_height = os.get_terminal_size() if sys.stdout.isatty() else (80, 24)
        
        if self.editor_mode:
            self._draw_editor(term_width, term_height)
            return

        col_width = 25
        
        # Calculate needed rows based on content
        content_rows = max(len(self.get_filtered_column(c)) for c in range(len(self.columns)))
        
        max_rows = content_rows
        if self.max_height:
            max_rows = min(max_rows, self.max_height)
        else:
            # Default max height is terminal height minus overhead
            max_rows = min(max_rows, max(1, term_height - 12))
            
        max_rows = max(max_rows, self.min_height)

        # Ensure scroll offsets are set and clamped for all columns
        for c in range(len(self.columns)):
            col_nodes = self.get_filtered_column(c)
            while len(self.scroll_offsets) <= c:
                self.scroll_offsets.append(0)
            idx = self.indices[c]
            if idx < self.scroll_offsets[c]:
                self.scroll_offsets[c] = idx
            elif idx >= self.scroll_offsets[c] + max_rows:
                self.scroll_offsets[c] = idx - max_rows + 1
            self.scroll_offsets[c] = max(0, min(self.scroll_offsets[c], len(col_nodes) - max_rows))

        sys.stdout.write("\033[H") # Move to top
        
        # Header & Breadcrumbs
        header_text = f" {self.title} | {self.get_breadcrumbs()} "
        header = header_text.center(term_width)
        sys.stdout.write(color_text(header, "1;37;44") + "\033[K\n")
        
        # Search bar if active
        if self.search_mode:
            search_line = f" SEARCH: {self.search_buffer}_ ".ljust(term_width)
            sys.stdout.write(color_text(search_line, "1;33;40") + "\033[K\n")
        else:
            sys.stdout.write(color_text("═" * term_width, "90") + "\033[K\n")

        # Main Columns
        for row_idx in range(max_rows):
            line = " "
            for col_idx in range(len(self.columns)):
                col_nodes = self.get_filtered_column(col_idx)
                actual_idx = row_idx + self.scroll_offsets[col_idx]
                if actual_idx < len(col_nodes):
                    node = col_nodes[actual_idx]
                    is_selected = (self.indices[col_idx] == actual_idx)
                    is_active_col = (self.active_col == col_idx)
                    
                    label = node.get_label()
                    is_current_setting = node.is_active()

                    if is_selected and is_active_col:
                        if self.edit_mode: 
                            prefix, style = "* ", "1;33;7"
                            from .nodes import InputNode
                            if isinstance(node, InputNode):
                                label = f"{node.get_label()}: {self.search_buffer}_"
                        else: prefix, style = "> ", "1;32;7"
                    elif is_selected: prefix, style = "- ", "1;34"
                    elif is_current_setting: prefix, style = "* ", "1;34"
                    else: prefix, style = "  ", "0"
                    
                    display_limit = col_width - 4
                    display_text = (label[:display_limit] + "..") if len(label) > display_limit else label
                    formatted = f"{prefix}{display_text:<{col_width-2}}"
                    line += color_text(formatted, style) + " | "
                else:
                    line += " " * col_width + " | "
            sys.stdout.write(line + "\033[K\n")

        sys.stdout.write(color_text("═" * term_width, "90") + "\033[K\n")
        
        # Status Area
        if self.status_callback:
            status_lines = self.status_callback()
            for sl in status_lines:
                sys.stdout.write(f"  {sl[:term_width-4]}\033[K\n")
        
        sys.stdout.write(color_text("─" * term_width, "90") + "\033[K\n")
        
        # Log/Help line
        if self.show_help:
            help_text = " [/] Search  [Enter] Edit/Action  [Arrows] Move  [H] Help  [Q] Quit ".center(term_width)
            sys.stdout.write(color_text(help_text, "1;37;42") + "\033[K\n")
        else:
            msg_to_show = self.message if self.message else "Use arrows to navigate, / to search, H for help."
            log_line = f"  {color_text('LOG:', '1;33')} {msg_to_show}"
            sys.stdout.write(log_line[:term_width+20] + "\033[K\n")
        
        # CLEAR EVERYTHING BELOW (prevents ghosting when menu shrinks)
        sys.stdout.write("\033[J")
        sys.stdout.flush()

    def _draw_editor(self, width, height):
        sys.stdout.write("\033[H")
        title = f" EDITOR: {self.title} (Ctrl+S: Save, Esc: Cancel) ".center(width)
        sys.stdout.write(color_text(title, "1;37;45") + "\033[K\n")
        sys.stdout.write(color_text("═" * width, "90") + "\033[K\n")
        
        for i in range(height - 6):
            if i < len(self.editor_buffer):
                line = self.editor_buffer[i]
                if i == self.editor_cursor[0]:
                    # Highlight cursor
                    col = self.editor_cursor[1]
                    part1 = line[:col]
                    char = line[col:col+1] if col < len(line) else " "
                    part2 = line[col+1:]
                    formatted = part1 + color_text(char, "7") + part2
                    sys.stdout.write(f" {i+1:2} | {formatted}\033[K\n")
                else:
                    sys.stdout.write(f" {i+1:2} | {line}\033[K\n")
            else:
                sys.stdout.write(f"    |\033[K\n")
        
        sys.stdout.write(color_text("═" * width, "90") + "\033[K\n")
        sys.stdout.write("\033[J")
        sys.stdout.flush()

    def suspend(self):
        sys.stdout.write("\033[?1000l\033[?25h\033[?1049l")
        sys.stdout.flush()

    def resume(self):
        sys.stdout.write("\033[?1049h\033[?1000h\033[?25l\033[H\033[J")
        sys.stdout.flush()

    def to_json(self) -> dict:
        if not self.root:
            from .bridge import yggdrasil_to_tui
            self.root = yggdrasil_to_tui(self.state, self.title)
        return {
            "title": self.title,
            "menu": self.root.to_json()
        }

    def find_node_by_path(self, path: str) -> Optional[BaseNode]:
        if not self.root:
            from .bridge import yggdrasil_to_tui
            self.root = yggdrasil_to_tui(self.state, self.title)
            
        def search(node):
            if node.get_path() == path:
                return node
            for child in node.get_children():
                res = search(child)
                if res:
                    return res
            return None
            
        return search(self.root)

    def execute_json_path(self, path: str, value: Any = None) -> dict:
        node = self.find_node_by_path(path)
        
        # Try direct update in background state tree
        parts = path.split("/")
        curr_state = self.state
        for part in parts[:-1]:
            if isinstance(curr_state, dict) and part in curr_state:
                curr_state = curr_state[part]
            else:
                curr_state = None
                break
        if curr_state is not None and isinstance(curr_state, dict) and parts[-1] in curr_state:
            curr_val = curr_state[parts[-1]]
            try:
                if isinstance(curr_val, bool):
                    if value is not None:
                        value = str(value).lower() in ("true", "1", "yes", "on")
                    else:
                        value = not curr_val
                elif isinstance(curr_val, int) and value is not None:
                    value = int(value)
                elif isinstance(curr_val, float) and value is not None:
                    value = float(value)
            except Exception:
                pass
            curr_state[parts[-1]] = value
            from .bridge import yggdrasil_to_tui
            self.root = yggdrasil_to_tui(self.state, self.title)
            return {"status": "success", "message": f"{path} updated directly in state", "value": value}

        if not node:
            return {"status": "error", "message": f"Path not found: {path}"}
            
        from .nodes import Action, Switch, Checkbox, Slider, InputNode
        
        try:
            if isinstance(node, Switch) or isinstance(node, Checkbox):
                if value is not None:
                    bool_val = str(value).lower() in ("true", "1", "yes", "on")
                    node.setter(bool_val)
                    return {"status": "success", "message": f"{path} set to {bool_val}", "value": bool_val}
                else:
                    new_val = not node.getter()
                    node.setter(new_val)
                    return {"status": "success", "message": f"{path} toggled to {new_val}", "value": new_val}
            elif isinstance(node, Slider):
                if value is not None:
                    node.setter(float(value))
                    return {"status": "success", "message": f"{path} set to {value}", "value": float(value)}
                else:
                    return {"status": "error", "message": "Value required for Slider"}
            elif isinstance(node, InputNode):
                msg = node.execute_input(str(value))
                return {"status": "success", "message": msg or f"{path} input executed", "value": value}
            elif isinstance(node, Action):
                msg = node.execute()
                return {"status": "success", "message": msg or f"{path} action executed"}
            else:
                return {"status": "error", "message": f"Cannot execute node type: {node.__class__.__name__}"}
        except Exception as e:
            return {"status": "error", "message": f"Execution failed: {e}"}

    def run(self):
        import json
        if "--json-schema" in sys.argv:
            print(json.dumps(self.to_json(), indent=2))
            return
            
        if "--json-exec" in sys.argv:
            idx = sys.argv.index("--json-exec")
            if idx + 1 < len(sys.argv):
                path = sys.argv[idx + 1]
                value = None
                if "--value" in sys.argv:
                    v_idx = sys.argv.index("--value")
                    if v_idx + 1 < len(sys.argv):
                        value = sys.argv[v_idx + 1]
                result = self.execute_json_path(path, value)
                print(json.dumps(result, indent=2))
                return

        from .bridge import set_active_tui, yggdrasil_to_tui
        set_active_tui(self)
        if not self.root:
            self.root = yggdrasil_to_tui(self.state, self.title)
            self.columns = [self.root.get_children()]
            self.indices = [0]
        self.resume()
        try:
            while self.running:
                self.draw()
                key = self._get_key()
                if not key: continue

                # Global keys
                if not self.edit_mode and not self.search_mode:
                    if key.lower() == 'q': break
                    if key.lower() == 'h': self.show_help = not self.show_help; continue
                    if key == '/': self.search_mode = True; self.search_buffer = ""; continue

                # Editor Mode
                if self.editor_mode:
                    col_nodes = self.get_filtered_column(self.active_col)
                    node = col_nodes[self.indices[self.active_col]]
                    from .nodes import EditorNode
                    
                    if key == '\x1b': # ESC
                        self.editor_mode = False; continue
                    elif key == '\x13': # Ctrl+S (might be tricky in raw, use special handling)
                        msg = node.save_content("\n".join(self.editor_buffer))
                        if msg: self.message = msg
                        self.editor_mode = False; continue
                    elif key == '\r' or key == '\n':
                        # New line
                        r, c = self.editor_cursor
                        current_line = self.editor_buffer[r]
                        self.editor_buffer[r] = current_line[:c]
                        self.editor_buffer.insert(r + 1, current_line[c:])
                        self.editor_cursor = [r + 1, 0]
                    elif key == '\x1b[A': # Up
                        self.editor_cursor[0] = max(0, self.editor_cursor[0] - 1)
                        self.editor_cursor[1] = min(len(self.editor_buffer[self.editor_cursor[0]]), self.editor_cursor[1])
                    elif key == '\x1b[B': # Down
                        self.editor_cursor[0] = min(len(self.editor_buffer) - 1, self.editor_cursor[0] + 1)
                        self.editor_cursor[1] = min(len(self.editor_buffer[self.editor_cursor[0]]), self.editor_cursor[1])
                    elif key == '\x1b[C': # Right
                        if self.editor_cursor[1] < len(self.editor_buffer[self.editor_cursor[0]]):
                            self.editor_cursor[1] += 1
                    elif key == '\x1b[D': # Left
                        self.editor_cursor[1] = max(0, self.editor_cursor[1] - 1)
                    elif key in ('\x7f', '\x08'): # Backspace
                        r, c = self.editor_cursor
                        if c > 0:
                            line = self.editor_buffer[r]
                            self.editor_buffer[r] = line[:c-1] + line[c:]
                            self.editor_cursor[1] -= 1
                        elif r > 0:
                            # Merge with previous line
                            prev_len = len(self.editor_buffer[r-1])
                            self.editor_buffer[r-1] += self.editor_buffer[r]
                            self.editor_buffer.pop(r)
                            self.editor_cursor = [r-1, prev_len]
                    elif len(key) == 1 and key.isprintable():
                        r, c = self.editor_cursor
                        line = self.editor_buffer[r]
                        self.editor_buffer[r] = line[:c] + key + line[c:]
                        self.editor_cursor[1] += 1
                    continue

                # Search Mode
                if self.search_mode:
                    if key == '\x1b': # Escape
                        self.search_mode = False; self.search_buffer = ""
                    elif key in ('\r', '\n'):
                        self.search_mode = False
                    elif key in ('\x7f', '\x08'): # Backspace
                        self.search_buffer = self.search_buffer[:-1]
                        self.indices[self.active_col] = 0
                    elif len(key) == 1 and key.isprintable():
                        self.search_buffer += key
                        self.indices[self.active_col] = 0
                    continue

                # Edit Mode (Slider / Input)
                if self.edit_mode:
                    col_nodes = self.get_filtered_column(self.active_col)
                    node = col_nodes[self.indices[self.active_col]]
                    from .nodes import Slider, InputNode
                    
                    if isinstance(node, Slider):
                        if key == '\x1b[C': node.adjust(node.step) # Right
                        elif key == '\x1b[D': node.adjust(-node.step) # Left
                        elif key in ('\r', '\n', '\x1b'): self.edit_mode = False
                    elif isinstance(node, InputNode):
                        if key in ('\r', '\n'):
                            msg = node.execute_input(self.search_buffer)
                            if msg: self.message = msg
                            self.edit_mode = False; self.search_buffer = ""
                        elif key == '\x1b': self.edit_mode = False; self.search_buffer = ""
                        elif key in ('\x7f', '\x08'): self.search_buffer = self.search_buffer[:-1]
                        elif len(key) == 1: self.search_buffer += key
                    continue

                # Normal Navigation
                col_nodes = self.get_filtered_column(self.active_col)
                if not col_nodes:
                    if key == '\x1b[D': # Left
                        self.active_col -= 1
                        self.columns = self.columns[:self.active_col+1]
                        self.indices = self.indices[:self.active_col+1]
                        self.scroll_offsets = self.scroll_offsets[:self.active_col+1]
                    continue

                if key == '\x1b[A': # Up
                    self.indices[self.active_col] = (self.indices[self.active_col] - 1) % len(col_nodes)
                elif key == '\x1b[B': # Down
                    self.indices[self.active_col] = (self.indices[self.active_col] + 1) % len(col_nodes)
                elif key == '\x1b[C' or key in ('\r', '\n'): # Right / Enter
                    node = col_nodes[self.indices[self.active_col]]
                    from .nodes import Folder, Slider, InputNode, EditorNode
                    
                    if isinstance(node, (Slider, InputNode)):
                        self.edit_mode = True
                        if isinstance(node, InputNode): self.search_buffer = ""
                    elif isinstance(node, EditorNode):
                        self.editor_mode = True
                        content = node.get_content()
                        self.editor_buffer = content.splitlines() if content else [""]
                        if not self.editor_buffer: self.editor_buffer = [""]
                        self.editor_cursor = [0, 0]
                    else:
                        children = node.get_children()
                        if children:
                            if len(self.columns) > self.active_col + 1:
                                self.columns[self.active_col+1] = children
                                self.indices[self.active_col+1] = 0
                                self.scroll_offsets[self.active_col+1] = 0
                            else:
                                self.columns.append(children)
                                self.indices.append(0)
                                self.scroll_offsets.append(0)
                            self.active_col += 1
                        else:
                            msg = node.execute()
                            if msg: self.message = msg
                elif key == '\x1b[D' and self.active_col > 0: # Left
                    self.active_col -= 1
                    self.columns = self.columns[:self.active_col+1]
                    self.indices = self.indices[:self.active_col+1]
                    self.scroll_offsets = self.scroll_offsets[:self.active_col+1]
                    self.search_buffer = ""
        finally:
            from .bridge import set_active_tui
            set_active_tui(None)
            self.suspend()
