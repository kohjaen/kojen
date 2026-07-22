import re
from typing import List, Union, Tuple

Token = str
Parsed = Union[str, List["Parsed"]]

def extract_tag_payload(s: str) -> str:
    # returns the first tag payload between <<< and >>>
    m = re.search(r'<<<(.*?)>>>', s, flags=re.DOTALL)
    if not m:
        raise ValueError("No <<< ... >>> tag found")
    return m.group(1).strip()

def tokenize(expr: str) -> List[str]:
    # Match operators/parentheses/atoms.
    # Atom is anything that isn't whitespace or one of ().
    token_re = re.compile(r"""
        \s*(
            AND|OR|NOT|
            \(|\)|
            [^\s()]+
        )
        """, re.VERBOSE | re.IGNORECASE)

    tokens = [t for t in token_re.findall(expr) if t and not t.isspace()]
    # Normalize operator case to upper
    tokens = [t.upper() if t.upper() in ("AND", "OR", "NOT") else t for t in tokens]
    return tokens

def strip_prefix(payload: str, prefix: str) -> str:
    # remove leading prefix token (prefix may be "IF", "ELSEIF", etc.)
    # Example payload: "IF (cond1 ...) OR cond2 ..."
    # We only strip the first token that matches the prefix ignoring case.
    # If you pass "IF", it will also strip "ELSEIF" if that is present and prefix is "IF"?:
    # Instead, we’ll just strip the first leading word (up to whitespace).
    # But you asked to pass a prefix; we support that specifically:
    prefix_re = re.compile(rf'^\s*{re.escape(prefix)}\b\s*', flags=re.IGNORECASE)
    if prefix_re.search(payload):
        return prefix_re.sub("", payload, count=1)
    # If prefix is "IF" and payload starts with "ELSEIF", allow it if prefix is "IF"
    # by stripping any leading IF/ELSEIF word; adjust as needed:
    if prefix.upper() == "IF":
        payload2 = re.sub(r'^\s*(?:IF|ELSEIF)\b\s*', '', payload, flags=re.IGNORECASE)
        return payload2
    # Otherwise fail early
    raise ValueError(f"Tag payload does not start with prefix {prefix!r}: {payload!r}")

def parse_parentheses(tokens: List[str]) -> Parsed:
    # Grammar-like parsing: parentheses create nested lists.
    # Outside parentheses we keep a flat list.
    #
    # We build lists where:
    #   - '(' starts a new list
    #   - ')' ends it
    #   - atoms/operators are appended
    stack: List[List[Parsed]] = [[]]

    for tok in tokens:
        if tok == '(':
            stack.append([])
        elif tok == ')':
            if len(stack) == 1:
                raise ValueError("Unmatched ')' in expression")
            completed = stack.pop()
            # Append the sub-expression list as an element
            stack[-1].append(completed)
        else:
            stack[-1].append(tok)

    if len(stack) != 1:
        raise ValueError("Unmatched '(' in expression")
    # If the whole expression wasn't wrapped, stack[0] is the top-level list
    return stack[0]

def parse_tag_expression(s: str, prefix: str) -> List:
    payload = extract_tag_payload(s)
    body = strip_prefix(payload, prefix)
    tokens = tokenize(body)
    parsed = parse_parentheses(tokens)

    # We want the output to be a list at top level.
    # parsed is List[...] already because parse_parentheses returns top-level list.
    return parsed

# -----------------------------------------

from typing import Callable, List, Union, Any

Parsed = Union[str, List["Parsed"]]

def eval_parsed_expr(expr: List[Parsed], condition_fn: Callable[[str], bool], *args) -> bool:
    """
    expr is the nested list produced by parse_all_tag_expressions() for one tag.
    condition_fn(atom_str) -> bool
    """

    # --- token stream conversion ---
    # expr already represents parentheses as nested lists. We'll recursively evaluate them
    # into a boolean token stream.
    def flatten_to_tokens(node: Parsed) -> List[Any]:
        if isinstance(node, list):
            # evaluate nested list to a bool, but still keep operators outside
            # For simplicity, we treat nested lists as a single atom token (bool)
            val = eval_parsed_expr(node, condition_fn, *args)
            return [val]
        # node is a string atom/operator
        u = node.upper() if isinstance(node, str) else node
        if u in ("AND", "OR", "NOT"):
            return [u]
        # otherwise it's a condition atom
        return [condition_fn(node, *args)]

    tokens = []
    for item in expr:
        tokens.extend(flatten_to_tokens(item))

    # --- shunting-yard to respect precedence ---
    # We will convert to RPN and then evaluate.
    prec = {"OR": 1, "AND": 2, "NOT": 3}
    right_assoc = {"NOT"}  # NOT is unary

    def to_rpn(toks: List[Any]) -> List[Any]:
        out = []
        ops = []
        for t in toks:
            if isinstance(t, bool):
                out.append(t)
            elif t in ("AND", "OR", "NOT"):
                while ops:
                    top = ops[-1]
                    if top in ("AND", "OR", "NOT"):
                        if (prec[top] > prec[t]) or (prec[top] == prec[t] and t not in right_assoc):
                            out.append(ops.pop())
                            continue
                    break
                ops.append(t)
            else:
                raise ValueError(f"Unexpected token: {t!r}")
        while ops:
            out.append(ops.pop())
        return out

    def eval_rpn(rpn: List[Any]) -> bool:
        stack = []
        for t in rpn:
            if isinstance(t, bool):
                stack.append(t)
            elif t == "NOT":
                if not stack:
                    raise ValueError("NOT missing operand")
                a = stack.pop()
                stack.append(not a)
            elif t in ("AND", "OR"):
                if len(stack) < 2:
                    raise ValueError(f"{t} missing operands")
                b = stack.pop()
                a = stack.pop()
                stack.append(a and b if t == "AND" else a or b)
            else:
                raise ValueError(f"Unexpected RPN token: {t!r}")
        if len(stack) != 1:
            raise ValueError(f"Invalid expression, stack={stack}")
        return stack[0]

    rpn = to_rpn(tokens)
    return eval_rpn(rpn)