def normalize(values):
    total = sum(values)
    if total == 0:
        return [0.0 for value in values]
    return [value / total for value in values]

print(normalize([2, 3, 5]))
