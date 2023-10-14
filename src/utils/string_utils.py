import re


def simplify_string(input_string: str) -> str:
    """Return a simplified version of the string with only alphanumeric characters in lowercase."""
    return ''.join(char for char in input_string if char.isalnum()).lower()


def clean_cell_value(cell_value: str) -> str:
    """Refine the cell value by eliminating unnecessary spaces and newline characters."""
    return re.sub(r'\s+', ' ', cell_value).strip().replace("’", "'")


def calculate_levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein distance between two strings."""
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def keyword_exists(content: str, keyword: str) -> bool:
    """Determine whether the keyword appears as a distinct word within the content."""
    return re.search(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE) is not None
