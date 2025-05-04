#Operations On NFA
# Allowed operations:
# (+) repetare odata sau mai multe ori
# (|) alternare 
# (*) repetare de zero sau mai multe ori
# (?) prezenta optionala
# (.) concatenarea

from finite_automata import NFA

#Functions for converting lambda_nfa to normal
def lambda_closure(lambda_nfa: NFA, state_set: set) -> set:
        stack = list(state_set)
        closure = set(state_set)
        while stack:
            state = stack.pop()
            if state in lambda_nfa.transitions and None in lambda_nfa.transitions[state]:
                for next_state in lambda_nfa.transitions[state][None]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return closure

def lambda_to_nfa(lambda_nfa: NFA) -> NFA:
    new_transitions = {}
    for state in lambda_nfa.states:
        closure = lambda_closure(lambda_nfa, {state})
        new_transitions[state] = {}

        for symbol in lambda_nfa.alphabet:
            next_states = set()
            for s in closure:
                if s in lambda_nfa.transitions and symbol in lambda_nfa.transitions[s]:
                    next_states.update(lambda_nfa.transitions[s][symbol])
            
            reachable = lambda_closure(lambda_nfa, next_states)
            if reachable:
                new_transitions[state][symbol] = reachable

    new_final_states = set()
    for state in lambda_nfa.states:
        closure = lambda_closure(lambda_nfa, {state})
        if closure.intersection(lambda_nfa.final_states):
            new_final_states.add(state)

    return NFA(
        states=lambda_nfa.states,
        alphabet=lambda_nfa.alphabet,
        transitions=new_transitions,
        start=lambda_nfa.start,
        final_states=new_final_states
    )

def rename_states(nfa: NFA, prefix: str) -> NFA:
    state_map = {s: f"{prefix}_{s}" for s in nfa.states}
    
    new_states = {state_map[s] for s in nfa.states}
    new_start = state_map[nfa.start]
    new_final_states = {state_map[s] for s in nfa.final_states}
    new_transitions = {}

    for s in nfa.transitions:
        new_transitions[state_map[s]] = {}
        for symbol in nfa.transitions[s]:
            new_transitions[state_map[s]][symbol] = {state_map[t] for t in nfa.transitions[s][symbol]}

    return NFA(new_states, nfa.alphabet, new_transitions, new_start, new_final_states)


def union(nfa1: NFA, nfa2: NFA) -> NFA:
    #rename the states
    nfa1_renamed = rename_states(nfa1, 'A')
    nfa2_renamed = rename_states(nfa2, 'B')

    new_start = 'new_start'
    new_states = nfa1_renamed.states.union(nfa2_renamed.states).union({new_start})
    new_alphabet = nfa1_renamed.alphabet.union(nfa2_renamed.alphabet)
    new_transitions = {**nfa1_renamed.transitions, **nfa2_renamed.transitions}

    #add lambda-move from new_start to the start states
    new_transitions[new_start] = {
        None: {nfa1_renamed.start, nfa2_renamed.start}
    }

    #new final states are final states of m1 + final states of m2
    new_final_states = nfa1_renamed.final_states.union(nfa2_renamed.final_states)

    return NFA(new_states, new_alphabet, new_transitions, new_start, new_final_states)


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


def kleene_star(nfa: NFA) -> NFA:
    #rename states
    nfa_renamed = rename_states(nfa, 'K')

    #add a new start and a new final state
    new_start = 'new_start'
    new_final = 'new_final'
    
    new_states = nfa_renamed.states.union({new_start, new_final})
    new_alphabet = nfa_renamed.alphabet
    new_transitions = {**nfa_renamed.transitions}

    # Add lambda-move from new start to new final
    new_transitions[new_start] = {None: {nfa_renamed.start, new_final}}
    
    # Add lambda move from every final state to starting state
    for final_state in nfa_renamed.final_states:
        if final_state not in new_transitions:
            new_transitions[final_state] = {}
        new_transitions[final_state][None] = {nfa_renamed.start, new_final}

    new_final_states = {new_final}

    return NFA(new_states, new_alphabet, new_transitions, new_start, new_final_states)

def kleene_plus(nfa: NFA) -> NFA:
    # a+ is aa*
    nfa_star = kleene_star(nfa)
    return concatenate(nfa, nfa_star)

def optional(nfa: NFA) -> NFA:
    # a? = a | lambda
    lambda_nfa = NFA(
        states={'lambda_start', 'lambda_final'},
        alphabet=nfa.alphabet,
        transitions={'lambda_start': {None: {'lambda_final'}}},
        start='lambda_start',
        final_states={'lambda_final'}
    )
    return union(nfa, lambda_nfa)

def make_literal_nfa(symbol: str) -> NFA:
    # simple 2 state automata for accepting one symbol
    start_state = 'q0'
    final_state = 'q1'
    states = {start_state, final_state}
    alphabet = {symbol}
    transitions = {
        start_state: {symbol: {final_state}}
    }
    return NFA(states, alphabet, transitions, start_state, {final_state})