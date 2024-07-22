import libcst as cst

# Original code
code = """
def hello_world():
    print("Hello, world!")
"""

# Parse code into a CST
module = cst.parse_module(code)

# Define a transformer to add logging
class AddLoggingTransformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # Add a print statement at the beginning of the function
        new_body = [
            cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.Call(func=cst.Name("print"), args=[cst.Arg(value=cst.SimpleString('"Entering function"'))]))]
            )
        ] + list(updated_node.body.body)
        return updated_node.with_changes(body=new_body)

# Apply the transformer
transformer = AddLoggingTransformer()
new_module = module.visit(transformer)

# Print the modified code
print(new_module.code)
