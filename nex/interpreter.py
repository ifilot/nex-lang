class Interpreter:
    """
    Tree-walking interpreter that evaluates AST nodes and produces values.
    """
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
        Evaluate a unary expression by first evaluating its operand,
        then applying the operator.
        """
        val = self.eval(node.expr)

        if node.op == '-':
            return -val
        elif node.op == '!':
            return not val
        else:
            raise NotImplementedError(f"Unsupported unary operator: {node.op}")
    
    def eval_Binary(self, node):
        """
        Evaluate a binary expression by evaluating both operands
        and applying the operator to their values.
        """
        left = self.eval(node.left)
        right = self.eval(node.right)

        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        else:
            raise NotImplementedError(f"Unsupported unary operator: {node.op}")