# agents/calculator_agent.py

import re
import math
import operator

def run(previous_data: dict) -> dict:
    """
    Calculator agent that performs mathematical calculations.
    Supports basic arithmetic, advanced math functions, and expression evaluation.
    """
    goal = previous_data.get("goal", "")
    
    # Extract mathematical expressions from the goal
    calculation_result = perform_calculation(goal)
    
    # Add calculation result to the data
    previous_data.update({"calculation": calculation_result})
    return previous_data

def perform_calculation(text: str) -> dict:
    """
    Perform mathematical calculations from text input.
    """
    try:
        # Clean and prepare the text
        text = text.lower().strip()
        
        # Remove trigger words
        text = re.sub(r'\b(calculate|compute|solve|what\s+is|find)\b', '', text, flags=re.IGNORECASE)
        text = text.strip()
        
        # Handle common math expressions
        expressions = extract_math_expressions(text)
        
        if not expressions:
            return {
                "success": False,
                "error": "No mathematical expression found",
                "input": text
            }
        
        results = []
        for expr in expressions:
            try:
                result = evaluate_expression(expr)
                results.append({
                    "expression": expr,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "expression": expr,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "success": True,
            "calculations": results,
            "input": text,
            "total_expressions": len(results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Calculation error: {str(e)}",
            "input": text
        }

def extract_math_expressions(text: str) -> list:
    """
    Extract mathematical expressions from text.
    """
    expressions = []
    
    # Handle special text-based math functions first
    # Handle "square root of X" or "sqrt of X"
    sqrt_pattern = r'(?:square\s+root\s+of|sqrt\s+of|√)\s+([\d.]+)'
    sqrt_matches = re.findall(sqrt_pattern, text, re.IGNORECASE)
    for match in sqrt_matches:
        expressions.append(f"sqrt({match})")
    
    # Handle "X to the power of Y" or "X power Y"
    power_pattern = r'([\d.]+)\s+(?:to\s+the\s+power\s+of|power\s+of?|raised\s+to)\s+([\d.]+)'
    power_matches = re.findall(power_pattern, text, re.IGNORECASE)
    for base, exp in power_matches:
        expressions.append(f"{base}**{exp}")
    
    # Handle "sine/sin of X", "cosine/cos of X", etc.
    trig_functions = ['sin', 'cos', 'tan', 'sine', 'cosine', 'tangent']
    for func in trig_functions:
        pattern = rf'{func}(?:e)?\s+of\s+([\d.]+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            func_name = 'sin' if 'sin' in func else 'cos' if 'cos' in func else 'tan'
            expressions.append(f"{func_name}({match})")
    
    # Handle "log of X" or "logarithm of X"
    log_pattern = r'(?:log(?:arithm)?)\s+of\s+([\d.]+)'
    log_matches = re.findall(log_pattern, text, re.IGNORECASE)
    for match in log_matches:
        expressions.append(f"log({match})")
    
    # Pattern for mathematical expressions (basic arithmetic)
    math_pattern = r'[0-9+\-*/().\s=^%√πe]+'
    
    # Common math function patterns
    function_patterns = [
        r'sqrt\(\s*[\d.]+\s*\)',  # sqrt(number)
        r'sin\(\s*[\d.]+\s*\)',   # sin(number)
        r'cos\(\s*[\d.]+\s*\)',   # cos(number)
        r'tan\(\s*[\d.]+\s*\)',   # tan(number)
        r'log\(\s*[\d.]+\s*\)',   # log(number)
        r'[\d.]+\s*\^\s*[\d.]+',  # power: number^number
        r'[\d.]+\s*\*\*\s*[\d.]+', # power: number**number
    ]
    
    # Look for explicit expressions with equals sign
    equals_match = re.search(r'(.+?)\s*=\s*(.+)', text)
    if equals_match:
        expressions.append(equals_match.group(1).strip())
    
    # Look for function patterns
    for pattern in function_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        expressions.extend(matches)
    
    # Look for basic arithmetic expressions
    # Remove already found expressions to avoid duplicates
    remaining_text = text
    for expr in expressions:
        remaining_text = remaining_text.replace(expr, '')
    
    # Find arithmetic expressions in remaining text
    arithmetic_matches = re.findall(r'[\d.]+\s*[+\-*/]\s*[\d.]+(?:\s*[+\-*/]\s*[\d.]+)*', remaining_text)
    expressions.extend(arithmetic_matches)
    
    # If no expressions found, try to extract just numbers and assume basic arithmetic
    if not expressions:
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if len(numbers) >= 2:
            # Look for operation context
            if any(word in text for word in ['plus', 'add', '+']):
                expressions.append(f"{numbers[0]} + {numbers[1]}")
            elif any(word in text for word in ['minus', 'subtract', '-']):
                expressions.append(f"{numbers[0]} - {numbers[1]}")
            elif any(word in text for word in ['times', 'multiply', '*', 'x']):
                expressions.append(f"{numbers[0]} * {numbers[1]}")
            elif any(word in text for word in ['divide', 'divided by', '/']):
                expressions.append(f"{numbers[0]} / {numbers[1]}")
            elif len(numbers) == 2:
                # Default to addition if no operation specified
                expressions.append(f"{numbers[0]} + {numbers[1]}")
    
    return [expr.strip() for expr in expressions if expr.strip()]

def evaluate_expression(expression: str) -> float:
    """
    Safely evaluate mathematical expressions.
    """
    # Clean the expression
    expression = expression.strip()
    
    # Replace common text with operators
    replacements = {
        'plus': '+',
        'minus': '-',
        'times': '*',
        'multiply': '*',
        'divided by': '/',
        'divide': '/',
        'power': '**',
        'to the power of': '**',
        '^': '**',
        '×': '*',
        '÷': '/',
        'π': str(math.pi),
        'pi': str(math.pi),
        'e': str(math.e),
        '√': 'sqrt'
    }
    
    for old, new in replacements.items():
        expression = expression.replace(old, new)
    
    # Handle sqrt function
    expression = re.sub(r'sqrt\(([^)]+)\)', r'math.sqrt(\1)', expression)
    
    # Handle other math functions
    math_functions = ['sin', 'cos', 'tan', 'log', 'log10', 'exp', 'floor', 'ceil', 'abs']
    for func in math_functions:
        pattern = f'{func}\\(([^)]+)\\)'
        replacement = f'math.{func}(\\1)'
        expression = re.sub(pattern, replacement, expression)
    
    # Create safe evaluation environment
    safe_dict = {
        "__builtins__": {},
        "math": math,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow
    }
    
    try:
        # Evaluate the expression
        result = eval(expression, safe_dict)
        return float(result)
    except Exception as e:
        raise ValueError(f"Cannot evaluate '{expression}': {str(e)}")

if __name__ == "__main__":
    # Test the calculator agent
    test_cases = [
        "calculate 2 + 3",
        "what is 15 * 4",
        "solve 100 / 5",
        "calculate sqrt(16)",
        "find 2^8",
        "compute sin(0)"
    ]
    
    for test in test_cases:
        print(f"\nTest: {test}")
        result = run({"goal": test})
        print(f"Result: {result['calculation']}")
