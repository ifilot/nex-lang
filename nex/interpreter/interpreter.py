from .environment import Environment

class Interpreter:
    """
    Tree-walking interpreter that evaluates AST nodes and produces values.
    """

    def __init__(self):
        """
        Default constructor: builds the environment associated with the
        interpeter.
        """
        self.env = Environment()

    def run(self, program):
        """
        Run a program by evaluating the list of statements
        """
        for node in program:
            self.exec(node)

    # -------------------------------------------------------------------------
    # STATEMENT EXECUTION
    # -------------------------------------------------------------------------

    def exec(self, node):
        """
        Execute a statement, dispatch to the appropriate exec_* method based on
        the runtime type of the node.
        """
        method = getattr(self, f"exec_{type(node).__name__}", self._exec_default)
        return method(node)

    def _exec_default(self, node):
        """
        Default execution; automatically raises a NotImplementedError to inform
        the user that there is no support (yet) for this type of node.
        """
        raise NotImplementedError(f"No exec for {type(node).__name__}")
    
    def exec_VarDecl(self, node):
        """
        Variable declaration
        """
        val = self.eval(node.initializer)
        return self.env.declare(node.name, val)
    
    def exec_Assign(self, node):
        """
        Assigns a value to variable or declares and initializes a new variable
        """
        val = self.eval(node.expr)
        self.env.assign(node.name, val)

    def exec_Print(self, node):
        """
        Built-in print function that outputs the result of an expression to the
        screen
        """
        val = self.eval(node.expr)
        print(val)

    def exec_Block(self, node):
        """
        Evaluate a block statement. Blocks result in scoping and variables
        declared inside a block statement shadow variables defined in a higher
        scope.
        """
        self.env.push()
        try:
            for stmt in node:
                self.exec(stmt)
        finally:
            self.env.pop()

    def exec_If(self, node):
        """
        Evaluate If statement.
        """
        val = self.eval(node.condition)
        if val:
            self.exec(node.then_branch)
        elif node.else_branch is not None:
            self.exec(node.else_branch)
    
    def exec_While(self, node):
        """
        Evaluate While statements.
        """
        while self.eval(node.condition):
            self.exec(node.body)

    # -------------------------------------------------------------------------
    # EXPRESSION EVALUATION
    # -------------------------------------------------------------------------

    def eval(self, node):
        """
        Dispatch to the appropriate eval_* method based on the runtime type of
        the node.
        """
        method = getattr(self, f"eval_{type(node).__name__}", self._eval_default)
        return method(node)
    
    def _eval_default(self, node):
        """
        Default evaluation; automatically raises a NotImplementedError to inform
        the user that there is no support (yet) for this type of node.
        """
        raise NotImplementedError(f"No eval for {type(node).__name__}")
    
    def eval_Literal(self, node):
        """
        Return the literal value directly.
        """
        return node.value
    
    def eval_Unary(self, node):
        """
        Evaluate a unary expression by first evaluating its operand, then
        applying the operator.
        """
        val = self.eval(node.expr)

        ops = {
            '-': lambda v: -v,
            '!': lambda v: not v,
        }

        try:
            return ops[node.op](val)
        except KeyError:
            raise NotImplementedError(f"Unsupported operator: {node.op}")
    
    def eval_Binary(self, node):
        """
        Evaluate a binary expression by evaluating both operands and applying
        the operator to their values.
        """
        left = self.eval(node.left)
        right = self.eval(node.right)

        # list binary operations
        ops = {
            '+': lambda l, r: l + r,
            '-': lambda l, r: l - r,
            '<': lambda l, r: l < r,
            '>': lambda l, r: l > r,
            '>=': lambda l, r: l >= r,
        }

        try:
            return ops[node.op](left, right)
        except KeyError:
            raise NotImplementedError(f"Unsupported operator: {node.op}")
        
    def eval_Variable(self, node):
        """
        Evaluates a variable and returns the value bound to it.
        """
        return self.env.lookup(node.name)