def roman_to_int(s: str) -> int:
    """
    Spec-First Implementation

    Rules extracted by LLM upfront:
    1. Valid characters: I, V, X, L, C, D, M
    2. V, L, D can never be repeated.
    3. I, X, C, M can be repeated max 3 times in a row.
    4. Subtraction rules:
       - I can only precede V or X
       - X can only precede L or C
       - C can only precede D or M
       - V, L, D can never be subtracted
    """
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

    valid_subtractions = {
        'I': {'V', 'X'},
        'X': {'L', 'C'},
        'C': {'D', 'M'}
    }
    non_repeatable = {'V', 'L', 'D'}

    total = 0
    i = 0
    n = len(s)

    while i < n:
        char = s[i]
        if char not in roman_values:
            raise ValueError(f"Invalid character: {char}")

        if char in non_repeatable and s.count(char) > 1:
            raise ValueError("Invalid roman numeral: V, L, D cannot be repeated")

        if i < n - 3 and char == s[i+1] == s[i+2] == s[i+3]:
            raise ValueError("Invalid roman numeral: too many consecutive identical characters")

        value = roman_values[char]

        if i + 1 < n and roman_values.get(s[i+1], 0) > value:
            next_char = s[i+1]
            if char not in valid_subtractions or next_char not in valid_subtractions[char]:
                raise ValueError("Invalid roman numeral: invalid subtraction")
            total += roman_values[next_char] - value
            i += 2
        else:
            total += value
            i += 1

    return total
