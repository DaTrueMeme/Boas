import operator

VALID_OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow
}

def math(num1, num2, operator, error_func, error_data):
    if not VALID_OPERATIONS.__contains__(operator):
        error_func(f"Operation '{operator}' is not valid.", error_data[0], error_data[1], "SyntaxError", target=operator)
        return num1
    
    result = None
    if operator == "/":
        if num1 == 0 or num2 == 0:
            result = 0
            return result
        
    result = VALID_OPERATIONS[operator](num1, num2)
    return result