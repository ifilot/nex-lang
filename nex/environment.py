class Environment:
    """
    Stores the environment of the interpreter
    """
    def __init__(self):
        """
        Default initializer (empty dictionary)
        """
        self.values = {}

    def declare(self, name, value):
        """
        Declare a new variable
        """
        self.values[name] = value

    def assign(self, name, value):
        """
        Assign a value to a variable
        """
        if name not in self.values:
            raise NameError(f"Undefined variable '{name}'")
        self.values[name] = value

    def lookup(self, name):
        """
        Look up the value associated to a variable
        """
        if name not in self.values:
            raise NameError(f"Undefined variable '{name}'")
        return self.values[name]