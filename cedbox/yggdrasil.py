import pandas as pd
import sqlite3

class Yggdrasil(dict):
    def __init__(self, leaf_behavior='overwrite'):
        """
        Initialize a new Yggdrasil tree.

        Args:
            leaf_behavior (str or callable): How to handle duplicate leaf nodes.
                If str, must be one of:
                    'overwrite': Replace existing value (default)
                    'append': Append to existing value if possible
                    'add': Add to existing value if both are numeric
                    'subtract': Subtract new value from existing value if both are numeric
                    'multiply': Multiply with existing value if both are numeric
                    'divide': Divide existing value by new value if both are numeric
                If callable, must be a function that takes two arguments (existing_value, new_value)
                and returns the value to be stored.
        """
        super().__init__()
        self.leaf_behavior = leaf_behavior

    def __getitem__(self, key):
        if key not in self:
            self[key] = self.__class__(leaf_behavior=self.leaf_behavior)
        return super().__getitem__(key)

    def __setitem__(self, key, values=None):
        if not isinstance(values, list) or not values:
            # Handle leaf node behavior if the key already exists
            if key in self and not isinstance(super().__getitem__(key), Yggdrasil):
                existing_value = super().__getitem__(key)

                # Check if leaf_behavior is a callable (custom function)
                if callable(self.leaf_behavior):
                    try:
                        # Call the custom function with existing and new values
                        new_value = self.leaf_behavior(existing_value, values)
                        super().__setitem__(key, new_value)
                    except Exception as e:
                        # If the custom function fails, fall back to overwrite
                        super().__setitem__(key, values)
                # Apply the specified behavior
                elif self.leaf_behavior == 'overwrite' or existing_value is None:
                    # Default behavior - just overwrite
                    super().__setitem__(key, values)
                elif self.leaf_behavior == 'append':
                    # Try to append values
                    try:
                        new_value = existing_value + values
                        super().__setitem__(key, new_value)
                    except (TypeError, ValueError):
                        # If append fails, fall back to overwrite
                        super().__setitem__(key, values)
                elif self.leaf_behavior == 'add' and values is not None:
                    # Try to add values numerically - only for numeric types
                    if (isinstance(existing_value, (int, float)) and 
                        isinstance(values, (int, float))):
                        new_value = existing_value + values
                        super().__setitem__(key, new_value)
                    else:
                        # For non-numeric types, fall back to overwrite
                        super().__setitem__(key, values)
                elif self.leaf_behavior == 'multiply' and values is not None:
                    # Try to multiply values - only for numeric types
                    if (isinstance(existing_value, (int, float)) and 
                        isinstance(values, (int, float))):
                        new_value = existing_value * values
                        super().__setitem__(key, new_value)
                    else:
                        # For non-numeric types, fall back to overwrite
                        super().__setitem__(key, values)
                elif self.leaf_behavior == 'subtract' and values is not None:
                    # Try to subtract values - only for numeric types
                    if (isinstance(existing_value, (int, float)) and 
                        isinstance(values, (int, float))):
                        new_value = existing_value - values
                        super().__setitem__(key, new_value)
                    else:
                        # For non-numeric types, fall back to overwrite
                        super().__setitem__(key, values)
                elif self.leaf_behavior == 'divide' and values is not None:
                    # Try to divide values - only for numeric types
                    if (isinstance(existing_value, (int, float)) and 
                        isinstance(values, (int, float))):
                        # Check for division by zero
                        if values == 0:
                            # For division by zero, fall back to overwrite
                            super().__setitem__(key, values)
                        else:
                            new_value = existing_value / values
                            super().__setitem__(key, new_value)
                    else:
                        # For non-numeric types, fall back to overwrite
                        super().__setitem__(key, values)
                else:
                    # Unknown behavior or incompatible types, fall back to overwrite
                    super().__setitem__(key, values)
            else:
                # Key doesn't exist or is a Yggdrasil instance, just set the value
                super().__setitem__(key, values)
            return

        if key not in self:
            super().__setitem__(key, self.__class__(leaf_behavior=self.leaf_behavior))

        value = values.pop(0)
        if values:
            self[key].__setitem__(value, values)
        else:
            # When setting a leaf node, just set the value
            # The behavior logic is already handled in the first part of this method
            self[key] = value

    def add_fiber(self, fiber):
        """
        Add a fiber (path) to the tree.

        Args:
            fiber: A list-like object or pandas Series representing a path in the tree.
                  The first element is the root node, and subsequent elements form the path.
        """
        # Convert pandas Series to list if necessary
        if isinstance(fiber, pd.Series):
            fiber = fiber.tolist()

        # Make a copy to avoid modifying the original
        fiber_copy = fiber.copy() if hasattr(fiber, 'copy') else list(fiber)

        sprout = fiber_copy.pop(0)
        self[sprout] = fiber_copy

    @classmethod
    def from_dataframe(cls, df, leaf_behavior='overwrite'):
        """
        Create a new Yggdrasil tree from a pandas DataFrame.

        Each row in the DataFrame will be added as a fiber to the tree.

        Args:
            df (pandas.DataFrame): The DataFrame to convert to a tree
            leaf_behavior (str or callable): How to handle duplicate leaf nodes
                                            (passed to Yggdrasil constructor)

        Returns:
            Yggdrasil: A new Yggdrasil tree containing the data from the DataFrame
        """
        tree = cls(leaf_behavior=leaf_behavior)

        # Iterate through each row in the DataFrame
        for _, row in df.iterrows():
            # Add the row as a fiber to the tree
            tree.add_fiber(row)

        return tree

    @classmethod
    def from_sql(cls, query, connection, leaf_behavior='overwrite'):
        """
        Create a new Yggdrasil tree from a SQL query.

        Executes the query and converts the result to a DataFrame,
        then creates a tree from the DataFrame.

        Args:
            query (str): The SQL query to execute
            connection: A database connection object (sqlite3.Connection, 
                       psycopg2.connection, etc.) or a connection string
            leaf_behavior (str or callable): How to handle duplicate leaf nodes
                                            (passed to Yggdrasil constructor)

        Returns:
            Yggdrasil: A new Yggdrasil tree containing the data from the query result
        """
        # Handle different types of connections
        if isinstance(connection, str):
            # Assume it's a SQLite connection string
            conn = sqlite3.connect(connection)
            df = pd.read_sql_query(query, conn)
            conn.close()
        else:
            # Assume it's an existing connection object
            df = pd.read_sql_query(query, connection)

        # Create a tree from the DataFrame
        return cls.from_dataframe(df, leaf_behavior=leaf_behavior)

    def print_tree(self, prefix="", is_root=True):
        """
        Print the tree structure like a directory tree with lines.

        Args:
            prefix (str): Prefix to use for the current line (for indentation)
            is_root (bool): Whether this is the root of the tree
        """
        # Get all keys in the current level
        keys = list(self.keys())

        if is_root and not keys:
            print("Empty tree")
            return

        # Process each key in the current level
        for i, key in enumerate(keys):
            is_last = i == len(keys) - 1
            connector = "└── " if is_last else "├── "

            # Print the current key with the appropriate connector
            print(f"{prefix}{connector}{key}")

            # Get the value for this key
            value = self[key]

            # Determine the prefix for the next level
            next_prefix = prefix + ("    " if is_last else "│   ")

            # If the value is another Yggdrasil instance, recursively print it
            if isinstance(value, Yggdrasil):
                value.print_tree(prefix=next_prefix, is_root=False)
            # Otherwise, print the value as a leaf node
            elif value is not None:
                print(f"{next_prefix}└── {value}")
