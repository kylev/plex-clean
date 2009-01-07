#=======================================================================
#
#   Python Lexical Analyser
#
#   Classes for building NFAs and DFAs
#
#=======================================================================

import sys

from Plex.Transitions import TransitionMap

LOWEST_PRIORITY = -sys.maxint

class Machine:
    """A collection of Nodes representing an NFA or DFA."""
    def __init__(self):
        self.states = list()
        self.initial_states = dict()
        self.next_state_number = 1

    def __del__(self):
        # TODO Do we need to do this explicitly?
        for state in self.states:
            state.destroy()

    def new_state(self):
        """Add a new state to the machine and return it."""
        s = Node()
        s.number = self.next_state_number
        self.states.append(s)

        self.next_state_number += 1
        return s

    def new_initial_state(self, name):
        state = self.new_state()
        self.make_initial_state(name, state)
        return state

    def make_initial_state(self, name, state):
        self.initial_states[name] = state

    def get_initial_state(self, name):
        return self.initial_states[name]

    def dump(self, file):
        file.write("Plex.Machine:\n")
        if self.initial_states is not None:
            file.write("   Initial states:\n")
            for (name, state) in self.initial_states.items():
                file.write("      '%s': %d\n" % (name, state.number))
        for s in self.states:
            s.dump(file)

class Node:
    """A state of an NFA or DFA."""
    transitions = None       # TransitionMap
    action = None            # Action
    action_priority = None   # integer
    number = 0               # for debug output
    epsilon_closure = None   # used by nfa_to_dfa()

    def __init__(self):
        # Preinitialise the list of empty transitions, because
        # the nfa-to-dfa algorithm needs it
        #self.transitions = {'':[]}
        self.transitions = TransitionMap()
        self.action_priority = LOWEST_PRIORITY

    def destroy(self):
        #print "Destroying", self ###
        self.transitions = None
        self.action = None
        self.epsilon_closure = None

    def add_transition(self, event, new_state):
        self.transitions.add(event, new_state)

    def link_to(self, state):
        """Add an epsilon-move from this state to another state."""
        self.add_transition('', state)

    def set_action(self, action, priority):
        """Make this an accepting state with the given action. If
        there is already an action, choose the action with highest
        priority."""
        if priority > self.action_priority:
            self.action = action
            self.action_priority = priority

    def get_action(self):
        return self.action

    def get_action_priority(self):
        return self.action_priority

    def is_accepting(self):
        return self.action is not None

    def __str__(self):
        return "State %d" % self.number

    def dump(self, out_file):
        # Header
        file.write("   State %d:\n" % self.number)
        # Transitions
        self.transitions.dump(out_file)
        # Action
        if self.action is not None:
            out_file.write("      %s [priority %d]\n" %
                           (self.action, self.action_priority))


class FastMachine:
    """FastMachine is a deterministic machine represented in a way that allows
    fast scanning.
    """
    new_state_template = {
        '': None, 'bol': None, 'eol': None, 'eof': None, 'else': None
    }

    def __init__(self, old_machine = None):
        self.initial_states = dict()
        self.states = list()
        self.next_number = 1 # for debugging
        if old_machine:
            self.old_to_new = old_to_new = {}
            for old_state in old_machine.states:
                new_state = self.new_state()
                old_to_new[old_state] = new_state
            for name, old_state in old_machine.initial_states.items():
                self.initial_states[name] = old_to_new[old_state]
            for old_state in old_machine.states:
                new_state = old_to_new[old_state]
                for event, old_state_set in old_state.transitions.items():
                    if old_state_set:
                        new_state[event] = old_to_new[old_state_set.keys()[0]]
                    else:
                        new_state[event] = None
                new_state['action'] = old_state.action

    def __del__(self):
        for state in self.states:
            state.clear()

    def new_state(self, action=None):
        number = self.next_number
        self.next_number = number + 1
        result = FastMachine.new_state_template.copy()
        result['number'] = number
        result['action'] = action
        self.states.append(result)
        return result

    def make_initial_state(self, name, state):
        self.initial_states[name] = state

    def add_transitions(self, state, event, new_state):
        if isinstance(event, tuple):
            code0, code1 = event
            if code0 == -sys.maxint:
                state['else'] = new_state
            elif code1 != sys.maxint:
                while code0 < code1:
                    state[chr(code0)] = new_state
                    code0 = code0 + 1
        else:
            state[event] = new_state

    def get_initial_state(self, name):
        return self.initial_states[name]

    def dump(self, file):
        file.write("Plex.FastMachine:\n")
        file.write("   Initial states:\n")
        for name, state in self.initial_states.items():
            file.write("      %s: %s\n" % (repr(name), state['number']))
        for state in self.states:
            self.dump_state(state, file)

    def dump_state(self, state, file):
        # Header
        file.write("   State %d:\n" % state['number'])
        # Transitions
        self.dump_transitions(state, file)
        # Action
        action = state['action']
        if action is not None:
            file.write("      %s\n" % action)

    def dump_transitions(self, state, file):
        chars_leading_to_state = {}
        special_to_state = {}
        for (c, s) in state.items():
            if len(c) == 1:
                chars = chars_leading_to_state.get(id(s), None)
                if chars is None:
                    chars = []
                    chars_leading_to_state[id(s)] = chars
                chars.append(c)
            elif len(c) <= 4:
                special_to_state[c] = s
        ranges_to_state = {}
        for state in self.states:
            char_list = chars_leading_to_state.get(id(state), None)
            if char_list:
                ranges = self.chars_to_ranges(char_list)
                ranges_to_state[ranges] = state
        ranges_list = ranges_to_state.keys()
        ranges_list.sort()
        for ranges in ranges_list:
            key = self.ranges_to_string(ranges)
            state = ranges_to_state[ranges]
            file.write("      %s --> State %d\n" % (key, state['number']))
        for key in ('bol', 'eol', 'eof', 'else'):
            state = special_to_state.get(key)
            if state:
                file.write("      %s --> State %d\n" % (key, state['number']))

    def chars_to_ranges(self, char_list):
        char_list.sort()
        i = 0
        n = len(char_list)
        result = []
        while i < n:
            c1 = ord(char_list[i])
            c2 = c1
            i = i + 1
            while i < n and ord(char_list[i]) == c2 + 1:
                i = i + 1
                c2 = c2 + 1
            result.append((chr(c1), chr(c2)))
        return tuple(result)

    def ranges_to_string(self, range_list):
        return ','.join(map(self.range_to_string, range_list))

    def range_to_string(self, (c1, c2)):
        if c1 == c2:
            return repr(c1)
        else:
            return "%s..%s" % (repr(c1), repr(c2))
