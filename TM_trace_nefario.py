#!/usr/bin/env python3

import csv
import sys
from collections import defaultdict, deque

class NondeterministicTuringMachine:
    def __init__(self, filename):
        self.transitions = defaultdict(list)  # Transitions will map (state, symbol) -> [(new_state, write_symbol, direction)]
        self.states = set()
        self.sigma = set()
        self.gamma = set()
        self.start_state = None
        self.accept_state = None
        self.reject_state = None
        self.max_depth = 100
        self.max_transitions = 1000
        self.load_machine(filename)
    
    def load_machine(self, filename):
        """Load NTM definition from a .csv file."""
        with open(filename, mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        self.name = rows[0][0]
        self.states = set(rows[1])
        self.sigma = set(rows[2])
        self.gamma = set(rows[3])
        self.start_state = rows[4][0]
        self.accept_state = rows[5][0]
        self.reject_state = rows[6][0]
        
        for transition in rows[7:]:
            current_state, read_symbol, new_state, write_symbol, direction = transition
            self.transitions[(current_state, read_symbol)].append((new_state, write_symbol, direction))

    def run(self, input_string, max_depth=100, max_transitions=1000):
        """Simulate the NTM with a breadth-first approach."""
        self.max_depth = max_depth
        self.max_transitions = max_transitions

        initial_config = ["", self.start_state, input_string]  # [left_tape, state, right_tape]
        tree = [[initial_config]]  # Tree of configurations
        transitions = 0

        while tree and transitions < self.max_transitions:
            current_level = tree[-1]
            next_level = []

            for left_tape, state, right_tape in current_level:
                if state == self.accept_state:
                    # Trace and halt immediately upon acceptance
                    self.print_accept_path(tree, len(tree) - 1)
                    return

                if state == self.reject_state:
                    continue  # Skip this branch if rejected

                # Read the symbol under the head
                head_symbol = right_tape[0] if right_tape else "_"
                transitions += 1

                if transitions > self.max_transitions:
                    print(f"Execution stopped after {self.max_transitions} transitions.")
                    return

                # Get transitions for the current state and head symbol
                possible_transitions = self.transitions.get((state, head_symbol), [])

                if not possible_transitions:
                    # No valid transitions, move to reject state
                    next_level.append([left_tape, self.reject_state, right_tape])
                    continue

                # Process valid transitions
                for new_state, write_symbol, direction in possible_transitions:
                    new_left_tape, new_right_tape = list(left_tape), list(right_tape)

                    # Write symbol
                    if new_right_tape:
                        new_right_tape[0] = write_symbol
                    else:
                        new_right_tape.append(write_symbol)

                    # Move head
                    if direction == "L":
                        if new_left_tape:
                            new_right_tape.insert(0, new_left_tape.pop())
                        else:
                            new_right_tape.insert(0, "_")
                    elif direction == "R":
                        if new_right_tape:
                            new_left_tape.append(new_right_tape.pop(0))
                        if not new_right_tape:
                            new_right_tape.append("_")

                    # Add new configuration
                    next_level.append(["".join(new_left_tape), new_state, "".join(new_right_tape)])


            # Add valid configurations to the tree
            if next_level:
                tree.append(next_level)

            # Stop if max depth reached
            if len(tree) > self.max_depth:
                print(f"Execution stopped after reaching max depth of {self.max_depth}.")
                return

            # Stop if all paths are rejecting
            if not any(config[1] != self.reject_state for config in next_level):
                print(f"String rejected in {len(tree) - 1} transitions.")
                return

        print(f"No valid paths found. Machine halted. configs explored: {len(tree)}")


    def print_accept_path(self, tree, depth):
        """Trace and print the path to the accept state."""
        print(f"String accepted in {depth} transitions.")
        num_configs = 0
        for level in range(depth + 1):
            for config in tree[level]:
                num_configs+=1
                print(f"Level {level}: {config}")
        print(f'num_configs: {num_configs-1}')

if __name__ == "__main__":
    machine_file = input("Enter the Turing machine file name: ")
    input_string = input("Enter the input string: ")
    max_depth = int(input("Enter max depth (default 100): ") or 100)
    max_transitions = int(input("Enter max transitions (default 1000): ") or 1000)

    ntm = NondeterministicTuringMachine(machine_file)
    ntm.run(input_string, max_depth, max_transitions)
