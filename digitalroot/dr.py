#!/usr/bin/env python3

def digitalroot(number):
    if number == 0:
        return 0
    else:
        return 1 + ((number -1) % 9)

roots = 10*[0]

for i in range(1000):
    root = digitalroot(i)
    print(f"DR of {i} is {root}")
    roots[root] += 1

print(roots)
