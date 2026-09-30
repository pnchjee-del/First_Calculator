import ast
import operator
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Supported safe operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(node):
    """Safely evaluate mathematical AST nodes without using eval()."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Invalid number literal")

    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op_type = type(node.op)
        if op_type in OPERATORS:
            if op_type is ast.Div and right == 0:
                raise ZeroDivisionError("Division by zero")
            return OPERATORS[op_type](left, right)
        raise ValueError("Unsupported operation")

    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in OPERATORS:
            return OPERATORS[op_type](operand)
        raise ValueError("Unsupported unary operator")

    else:
        raise ValueError("Invalid mathematical expression")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}
    expr = data.get("expression", "").strip()

    if not expr:
        return jsonify({"result": "0"})

    try:
        # Parse expression into an AST tree
        parsed = ast.parse(expr, mode="eval")
        result = safe_eval(parsed.body)

        # Format integer results cleanly (e.g. 5.0 -> 5)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        else:
            result = round(result, 8)

        return jsonify({"result": str(result)})
    except ZeroDivisionError:
        return jsonify({"result": "Error: Div by 0"}), 400
    except Exception:
        return jsonify({"result": "Error"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)