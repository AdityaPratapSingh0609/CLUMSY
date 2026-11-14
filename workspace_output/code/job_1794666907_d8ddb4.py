def fibonacci(n: int) -> list[int]:
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

if __name__ == '__main__':
    print('Fibonacci(10):', fibonacci(10))
