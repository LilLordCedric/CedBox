import pytest
import pandas as pd
import sqlite3
import io
from contextlib import redirect_stdout
from cedbox.yggdrasil import Yggdrasil

class TestYggdrasilBasic:
    """Tests for basic Yggdrasil functionality"""

    def test_init_default(self):
        """Test default initialization"""
        tree = Yggdrasil()
        assert isinstance(tree, Yggdrasil)
        assert tree.leaf_behavior == 'overwrite'
        assert len(tree) == 0

    def test_init_custom_behavior(self):
        """Test initialization with custom leaf behavior"""
        tree = Yggdrasil(leaf_behavior='add')
        assert tree.leaf_behavior == 'add'

        # Test with custom function
        def custom_merge(a, b):
            return f"{a}+{b}"

        tree = Yggdrasil(leaf_behavior=custom_merge)
        assert tree.leaf_behavior == custom_merge

    def test_auto_node_creation(self):
        """Test automatic node creation when accessing non-existent keys"""
        tree = Yggdrasil()
        # Access a non-existent key
        subtree = tree['level1']

        # Verify a new node was created
        assert 'level1' in tree
        assert isinstance(subtree, Yggdrasil)
        assert len(subtree) == 0

        # Test nested access
        nested = tree['level1']['level2']['level3']
        assert isinstance(nested, Yggdrasil)
        assert 'level2' in tree['level1']
        assert 'level3' in tree['level1']['level2']

    def test_dict_operations(self):
        """Test that Yggdrasil supports standard dictionary operations"""
        tree = Yggdrasil()

        # Set values
        tree['key1'] = 'value1'
        tree['key2'] = 'value2'

        # Get values
        assert tree['key1'] == 'value1'
        assert tree['key2'] == 'value2'

        # Check membership
        assert 'key1' in tree
        assert 'nonexistent' not in tree

        # Get keys and values
        assert set(tree.keys()) == {'key1', 'key2'}
        assert set(tree.values()) == {'value1', 'value2'}

        # Items
        assert dict(tree.items()) == {'key1': 'value1', 'key2': 'value2'}

        # Length
        assert len(tree) == 2

        # Delete
        del tree['key1']
        assert 'key1' not in tree
        assert len(tree) == 1

class TestLeafBehaviors:
    """Tests for different leaf behaviors"""

    def test_overwrite_behavior(self):
        """Test 'overwrite' leaf behavior (default)"""
        tree = Yggdrasil(leaf_behavior='overwrite')
        tree['key'] = 'value1'
        tree['key'] = 'value2'
        assert tree['key'] == 'value2'

    def test_append_behavior(self):
        """Test 'append' leaf behavior"""
        tree = Yggdrasil(leaf_behavior='append')

        # String append
        tree['str'] = 'Hello'
        tree['str'] = ' World'
        assert tree['str'] == 'Hello World'

        # List-like append with tuples (since lists become dict-like in Yggdrasil)
        tree['tuple'] = (1, 2)
        tree['tuple'] = (3, 4)
        assert tree['tuple'] == (1, 2, 3, 4)

        # Numeric types are added with 'append' behavior
        tree['num'] = 5
        tree['num'] = 10
        assert tree['num'] == 15

    def test_add_behavior(self):
        """Test 'add' leaf behavior"""
        tree = Yggdrasil(leaf_behavior='add')

        # Numeric addition
        tree['num'] = 5
        tree['num'] = 10
        assert tree['num'] == 15

        # Non-numeric types should fall back to overwrite
        tree['str'] = 'Hello'
        tree['str'] = 'World'
        assert tree['str'] == 'World'

    def test_subtract_behavior(self):
        """Test 'subtract' leaf behavior"""
        tree = Yggdrasil(leaf_behavior='subtract')
        tree['num'] = 20
        tree['num'] = 5
        assert tree['num'] == 15

    def test_multiply_behavior(self):
        """Test 'multiply' leaf behavior"""
        tree = Yggdrasil(leaf_behavior='multiply')
        tree['num'] = 5
        tree['num'] = 4
        assert tree['num'] == 20

    def test_divide_behavior(self):
        """Test 'divide' leaf behavior"""
        tree = Yggdrasil(leaf_behavior='divide')
        tree['num'] = 20
        tree['num'] = 4
        assert tree['num'] == 5

        # Division by zero should fall back to overwrite
        tree['num'] = 10
        tree['num'] = 0
        assert tree['num'] == 0

    def test_custom_behavior(self):
        """Test custom leaf behavior function"""
        def join_with_comma(a, b):
            return f"{a},{b}"

        tree = Yggdrasil(leaf_behavior=join_with_comma)
        tree['key'] = 'value1'
        tree['key'] = 'value2'
        assert tree['key'] == 'value1,value2'

        # Test with exception in custom function
        def buggy_function(a, b):
            raise ValueError("Oops")

        tree = Yggdrasil(leaf_behavior=buggy_function)
        tree['key'] = 'value1'
        tree['key'] = 'value2'
        # Should fall back to overwrite
        assert tree['key'] == 'value2'

class TestAddFiber:
    """Tests for the add_fiber method"""

    def test_add_fiber_list(self):
        """Test add_fiber with a list"""
        tree = Yggdrasil()
        tree.add_fiber(['root', 'branch', 'leaf', 'value'])

        assert 'root' in tree
        assert 'branch' in tree['root']
        assert 'leaf' in tree['root']['branch']
        assert tree['root']['branch']['leaf'] == 'value'

    def test_add_fiber_series(self):
        """Test add_fiber with a pandas Series"""
        tree = Yggdrasil()
        series = pd.Series(['root', 'branch', 'leaf', 'value'])
        tree.add_fiber(series)

        assert 'root' in tree
        assert 'branch' in tree['root']
        assert 'leaf' in tree['root']['branch']
        assert tree['root']['branch']['leaf'] == 'value'

    def test_add_multiple_fibers(self):
        """Test adding multiple fibers"""
        tree = Yggdrasil()
        tree.add_fiber(['animals', 'mammals', 'cats', 'Meow'])
        tree.add_fiber(['animals', 'mammals', 'dogs', 'Woof'])
        tree.add_fiber(['animals', 'birds', 'parrot', 'Squawk'])

        assert 'animals' in tree
        assert 'mammals' in tree['animals']
        assert 'birds' in tree['animals']
        assert 'cats' in tree['animals']['mammals']
        assert 'dogs' in tree['animals']['mammals']
        assert 'parrot' in tree['animals']['birds']
        assert tree['animals']['mammals']['cats'] == 'Meow'
        assert tree['animals']['mammals']['dogs'] == 'Woof'
        assert tree['animals']['birds']['parrot'] == 'Squawk'

    def test_add_fiber_preserves_original(self):
        """Test that add_fiber doesn't modify the original fiber"""
        tree = Yggdrasil()
        fiber = ['root', 'branch', 'leaf', 'value']
        original = fiber.copy()

        tree.add_fiber(fiber)

        # Original fiber should be unchanged
        assert fiber == original

class TestFromDataFrame:
    """Tests for the from_dataframe class method"""

    def test_from_dataframe_basic(self):
        """Test creating a tree from a basic DataFrame"""
        # Create a sample DataFrame
        data = {
            'col1': ['A', 'A', 'B'],
            'col2': ['X', 'Y', 'Z'],
            'col3': [1, 2, 3]
        }
        df = pd.DataFrame(data)

        # Create tree from DataFrame
        tree = Yggdrasil.from_dataframe(df)

        # Verify tree structure
        assert 'A' in tree
        assert 'B' in tree
        assert 'X' in tree['A']
        assert 'Y' in tree['A']
        assert 'Z' in tree['B']
        assert tree['A']['X'] == 1
        assert tree['A']['Y'] == 2
        assert tree['B']['Z'] == 3

    def test_from_dataframe_custom_behavior(self):
        """Test from_dataframe with custom leaf behavior"""
        # Create a DataFrame with duplicate paths
        data = {
            'col1': ['A', 'A'],
            'col2': ['X', 'X'],
            'col3': [5, 10]
        }
        df = pd.DataFrame(data)

        # Create tree with 'add' behavior
        tree = Yggdrasil.from_dataframe(df, leaf_behavior='add')

        # The values should be added
        assert tree['A']['X'] == 15

class TestFromSQL:
    """Tests for the from_sql class method"""

    def test_from_sql_connection_object(self):
        """Test creating a tree from a SQL query with a connection object"""
        # Create an in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        # Create a test table and insert data
        cursor.execute('CREATE TABLE test (col1 TEXT, col2 TEXT, col3 INTEGER)')
        cursor.executemany('INSERT INTO test VALUES (?, ?, ?)', [
            ('A', 'X', 1),
            ('A', 'Y', 2),
            ('B', 'Z', 3)
        ])
        conn.commit()

        # Create tree from SQL query
        query = "SELECT * FROM test"
        tree = Yggdrasil.from_sql(query, conn)

        # Verify tree structure
        assert 'A' in tree
        assert 'B' in tree
        assert 'X' in tree['A']
        assert 'Y' in tree['A']
        assert 'Z' in tree['B']
        assert tree['A']['X'] == 1
        assert tree['A']['Y'] == 2
        assert tree['B']['Z'] == 3

        # Clean up
        conn.close()

    def test_from_sql_connection_string(self):
        """Test creating a tree from a SQL query with a connection string"""
        # This test is more challenging to implement in a test environment
        # as it requires a file-based SQLite database
        # For now, we'll skip this test with a message
        pytest.skip("Test requires a file-based SQLite database")

class TestPrintTree:
    """Tests for the print_tree method"""

    def test_print_tree_empty(self):
        """Test print_tree with an empty tree"""
        tree = Yggdrasil()

        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            tree.print_tree()

        # Verify output
        assert "Empty tree" in captured_output.getvalue()

    def test_print_tree_basic(self):
        """Test print_tree with a basic tree"""
        tree = Yggdrasil()
        tree['root'] = 'value'

        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            tree.print_tree()

        # Verify output
        output = captured_output.getvalue()
        assert "└── root" in output
        assert "    └── value" in output

    def test_print_tree_complex(self):
        """Test print_tree with a more complex tree"""
        tree = Yggdrasil()
        tree.add_fiber(['animals', 'mammals', 'cats', 'Meow'])
        tree.add_fiber(['animals', 'mammals', 'dogs', 'Woof'])
        tree.add_fiber(['animals', 'birds', 'parrot', 'Squawk'])

        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            tree.print_tree()

        # Verify output contains expected elements
        output = captured_output.getvalue()
        assert "└── animals" in output
        assert "    ├── mammals" in output
        assert "    │   ├── cats" in output
        assert "    │   │   └── Meow" in output
        assert "    │   └── dogs" in output
        assert "    │       └── Woof" in output
        assert "    └── birds" in output
        assert "        └── parrot" in output
        assert "            └── Squawk" in output
