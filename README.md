# RegexToDfa
This application converts a regular expression into a finite automata that can check acceptance of words.

## Running instructions
This application requires [python3](https://www.python.org/downloads).<br>
To run the application, you must execute the following in the project directory: <br>
```
python3 main.py 
```
To load your tests, edit the json file: *data.json*. The format for tests is as follows:
```
{
    "name": "R19",
    "regex": "(a|b)+c+d*",
    "test_strings": [
      { "input": "abc", "expected": true },
      { "input": "aabcc", "expected": true },
      { "input": "bbccddd", "expected": true },
      { "input": "cc", "expected": false },
      { "input": "d", "expected": false }
    ]
  }
```
Then, the program parses the json file and outputs the state of every test:
```
=== Testing R18: '(a(bc)?d)+' ===
Postfix: abc.?.d.+
'ad' -> True
'abcd' -> True
'adbcd' -> False
'abcbcd' -> False
```
And how many tests passed: `86 passed and 0 failed`

## Structure
The implementation goes through the following steps:
* Regular expression - input
* Regular expression in postfix form (via Shunting-Yard algorithm) 
* lambda-NFA constructed from operations 
* NFA obtained by removing lambda states
* DFA (via subset construction) - output

The application is structured in 3 files: *operations.py*, *finite_automata.py* and *main.py*.
### Operations on NFA
*operations.py* contains functions that are useful for making operations between two NFAs. For example:
```
#concatenation of two DFAs
def concatenate(nfa1: NFA, nfa2: NFA) -> NFA:
    #rename the states
    nfa1_renamed = rename_states(nfa1, 'A')
    nfa2_renamed = rename_states(nfa2, 'B')

    new_start = nfa1_renamed.start
    new_states = nfa1_renamed.states.union(nfa2_renamed.states)
    new_alphabet = nfa1_renamed.alphabet.union(nfa2_renamed.alphabet)
    new_transitions = {**nfa1_renamed.transitions, **nfa2_renamed.transitions}

    #add lambda move from all final states of m1 to starting state of m2
    for final_state in nfa1_renamed.final_states:
        if final_state not in new_transitions:
            new_transitions[final_state] = {}
        new_transitions[final_state][None] = {nfa2_renamed.start}
    
    #final states are the final states of m2
    new_final_states = nfa2_renamed.final_states

    return NFA(new_states, new_alphabet, new_transitions, new_start, new_final_states)
```
The regex is of the form (a|b)+c+d* and the concatenation is implicit. So, before converting to postfix, we insert `.` (dot) where there is a concatenation and treat this as one of the operations. <br><br>
The operations that appear in the regex expressions the program accepts are:
| Operator | Meaning              | NFA Behavior                                              |                                                       |
| -------- | -------------------- | --------------------------------------------------------- | ----------------------------------------------------- |
| `+`      | One or more (`a+`)   | Concatenate with Kleene star: `A . A*`.                   |                                                       |
| &#124;   | Alternation &#124;   | Reunion. Add lambda-transitions to both NFAs from a new start state. |                                                       |
| `*`      | Zero or more (`a*`)  | Loop via lambda-transitions.                               |                                                       |
| `?`      | Optional - Zero or one (`a?`)      | Add lambda-transition to skip the operand.   |                                                       |
| `.`      | Concatenation (`ab`) | Link the final states of first NFA to start of second NFA via a lambda-transition.|                                 |



### Implementation of finite machines
*finite_automata.py* contains code related to a NFA object:
```
class NFA:
    def __init__(self, states: set, alphabet:set, transitions:dict, start:str, final_states:set):
        pass
    def print(self):
        pass
    def checkAcceptance(self, word: str) -> bool:
        pass
    def isDeterministic(self) -> bool:
        pass
```
### Testing and utility functions
*main.py* contains the code for: 
* converting an expression to postfix form using [Shunting-Yard](https://en.wikipedia.org/wiki/Shunting_yard_algorithm).
* converting the post-fix form to minimized DFA.
* parsing the test for the data given as input in *data.json*.
