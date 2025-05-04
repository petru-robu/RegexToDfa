import json
from operations import *

def add_concatenation_symbols(reg_exp: str) -> str:
    result = []
    for i in range(len(reg_exp)):
        ch1 = reg_exp[i]
        result.append(ch1)

        if i + 1 < len(reg_exp):
            ch2 = reg_exp[i + 1]
            if(
                (ch1 not in '(|' and ch2 not in '|)*+?)') or
                (ch1 in '*+?' and ch2 not in '|)*+?)(') or
                (ch1 == ')' and ch2 not in '|)*+?)')
            ):
                result.append('.')
    return ''.join(result)


def convert_to_postfix(reg_exp: str) -> str:
    #Shunting Yard
    precedence = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
    right_associative = {'*', '+', '?'}
    
    output = []
    stack = [] 
    
    reg_exp = add_concatenation_symbols(reg_exp)
    
    for token in reg_exp:
        if token.isalnum():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while (
                stack and stack[-1] != '(' and (
                    precedence[stack[-1]] > precedence[token] or
                    (precedence[stack[-1]] == precedence[token] and token not in right_associative)
                )
            ):
                output.append(stack.pop())
            stack.append(token)
            
    while stack:
        output.append(stack.pop())

    return ''.join(output)


def postfix_regex_to_nfa(postfix: str) -> NFA:
    stack = []
    for token in postfix:
        if token in {'*', '+', '?', '.', '|'}:
            if token == '*':
                nfa = stack.pop()
                stack.append(kleene_star(nfa))
            elif token == '+':
                nfa = stack.pop()
                stack.append(kleene_plus(nfa))
            elif token == '?':
                nfa = stack.pop()
                stack.append(optional(nfa))
            elif token == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(concatenate(nfa1, nfa2))
            elif token == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(union(nfa1, nfa2))
        else:
            #New symbol
            stack.append(make_literal_nfa(token))

    if len(stack) != 1:
        raise ValueError("Invalid postfix regex")

    return lambda_to_nfa(stack.pop())


def run_regex_tests_from_json(json_file):
    with open(json_file, 'r') as f:
        test_batches = json.load(f)

    total_passed = 0
    total_failed = 0

    for batch in test_batches:
        name = batch['name']
        regex = batch['regex']
        tests = batch['test_strings']

        print(f"\n=== Testing {name}: '{regex}' ===")

        postfix = convert_to_postfix(regex)
        print(f"Postfix: {postfix}")

        nfa = postfix_regex_to_nfa(postfix)
        if nfa == None:
            print(f"Failed to build NFA for {regex}: {e}")
            continue
        
        for test in tests:
            word = test['input']
            expected = test['expected']

            result = nfa.checkAcceptance(word)

            if result == expected:
                print(f"'{word}' -> {result}")
                total_passed += 1
            else:
                print(f"'{word}' -> {result}, expected {expected}")
                total_failed += 1

    print(f'{total_passed} passed and {total_failed} failed')


if __name__ == '__main__':
    run_regex_tests_from_json('data.json')

