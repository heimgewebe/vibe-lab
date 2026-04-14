def roman_to_int(s: str) -> int:
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

    # Validation Rules (TDD Vibe enforces robust validation upfront because tests demand it)
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

        # Check non-repeatable
        if char in non_repeatable:
            if s.count(char) > 1:
                 raise ValueError("Invalid roman numeral: V, L, D cannot be repeated")

        # Check max 3 consecutive identical characters
        if i < n - 3 and char == s[i+1] == s[i+2] == s[i+3]:
            raise ValueError("Invalid roman numeral: too many consecutive identical characters")

        value = roman_values[char]

        # Subtraction check
        if i + 1 < n and roman_values[s[i+1]] > value:
            next_char = s[i+1]
            if char not in valid_subtractions or next_char not in valid_subtractions[char]:
                raise ValueError("Invalid roman numeral: invalid subtraction")
            total += roman_values[next_char] - value
            i += 2 # Skip the next char
        else:
            total += value
            i += 1

    return total
