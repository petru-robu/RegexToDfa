#Finite Automata Implementation
class NFA:
    def __init__(self, states: set, alphabet:set, transitions:dict, start:str, final_states:set):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start = start
        self.final_states = final_states

    def print(self):
        print(f'-----NFA Description-----')
        print(f'States: {', '.join(self.states)}')
        print(f'Alphabet: {', '.join(self.alphabet)}')
        print('Transitions: ')
        for transition in self.transitions:
            edges = self.transitions[transition]
            for edge_letter in edges:
                print(f'({transition},{edge_letter})->{edges[edge_letter]}', end = "; ")
            print()
        print(f'Starts from: {self.start}')
        print(f'Final States: {', '.join(self.final_states)}')
        print(f'is DFA? -> {self.isDeterministic()}')

    def checkAcceptance(self, word: str) -> bool:
        #print("-----Checking word-----")
        letters = list(word)
        for letter in set(letters):
            if letter not in self.alphabet:
                return False
            
        curr_states = set()
        curr_states.add(self.start)

        i = 0
        while i < len(letters):
            states_to_search = curr_states.copy()
            while len(curr_states) > 0:
                curr_states.pop()

            for state in states_to_search:
                if state in self.transitions and letters[i] in self.transitions[state] and self.transitions[state][letters[i]] != None:
                    for next_state in self.transitions[state][letters[i]]:
                        curr_states.add(next_state)
            
            #print(states_to_search, ',', letters[i], '-> ', curr_states)
            i += 1
        
        for state in curr_states:
            if state in set(self.final_states):
                return True
        return False

    def isDeterministic(self) -> bool:
        for transition in self.transitions:
            edges = self.transitions[transition]
            for edge_letter in edges:
                if len(self.transitions[transition][edge_letter]) > 1:
                    return False
        return True