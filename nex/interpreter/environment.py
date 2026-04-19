class Environment:
    """
    Stores the environment of the interpreter
    """

    def __init__(self):
        """
        Default initializer (empty dictionary)
        """
        self.values = [{}]

    def push(self):
        """
        Push a new environment onto the stack
        """
        self.values.append({})

    def pop(self):
        """
        Pop an environment from the stack
        """
        if len(self.values) == 1:
            raise RuntimeError("Cannot pop global environment")
        self.values.pop()

    def declare(self, name, value):
        """
        Declare a new variable
        """
        if name in self.values[-1]:
            raise NameError(f"Redeclaration of variable '{name}' in the current scope")
        self.values[-1][name] = value

    def assign(self, name, value):
        """
        Assign a value to a variable
        """
        for env in reversed(self.values):
            if name in env:
                env[name] = value
                return
        raise NameError(f"Undefined variable '{name}'")

    def lookup(self, name):
        """
        Look up the value associated to a variable
        """
        for env in reversed(self.values):
            if name in env:
                return env[name]
        raise NameError(f"Undefined variable '{name}'")
