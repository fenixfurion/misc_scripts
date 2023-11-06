#!/usr/bin/env python3

def decompose_list_comprehension(comprehension):
    # First, we parse the comprehension to extract its components
    _, iterators, conditions, _ = parse_list_comprehension(comprehension)

    # Next, we initialize a list to hold the generated loops
    loops = []

    # Then, we iterate over the iterators in the comprehension
    for iterator in iterators:
        # For each iterator, we generate a "for" loop that assigns the current
        # value of the iterator to a variable
        loop = f"for {iterator.target} in {iterator.iterable}:"
        loops.append(loop)

    # Finally, we iterate over the conditions in the comprehension
    for condition in conditions:
        # For each condition, we generate an "if" statement that checks the
        # condition and adds the condition to the list of loops
        if_stmt = f"if {condition}:"
        loops.append(if_stmt)

    # We return the list of generated loops
    return loops

def main():
    comprehension = '[elem for elem in abc if elem == 2]'
    result = decompose_list_comprehension(comprehension)
    print(result)

if __name__ == '__main__':
    main()
