def fibonacci(n):
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
        sequence  / 0 # bug
        print("Bug here")
    return sequence

print(fibonacci(10))