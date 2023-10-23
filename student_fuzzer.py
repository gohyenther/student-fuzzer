from fuzzingbook import GreyboxFuzzer as gbf
from fuzzingbook import Coverage as cv
from fuzzingbook import MutationFuzzer as mf

import traceback
import numpy as np
import time
import random

from bug import entrypoint
from bug import get_initial_corpus

## You can re-implement the coverage class to change how
## the fuzzer tracks new behavior in the SUT

class MyCoverage(cv.Coverage):

    def coverage(self):
        # <your implementation here>
        
        # purpose: to track the sequence of executions
        traces = []
        for trace in self.trace():
            traces.append(trace)
        
        return traces


## You can re-implement the runner class to change how
## the fuzzer tracks new behavior in the SUT

class MyRunner(mf.FunctionRunner):

    def run_function(self, inp):
        # <your implementation here>
        with MyCoverage() as cover:
            try:
                result = super().run_function(inp)
            except Exception as exc:
                self._coverage = cover.coverage()
                raise exc

        self._coverage = cover.coverage()
        return result

    def coverage(self):
        # <your implementation here>
        return self._coverage


## You can re-implement the fuzzer class to change your
## fuzzer's overall structure

# class MyFuzzer(gbf.GreyboxFuzzer):
#
#     def reset(self):
#           <your implementation here>
#
#     def run(self, runner: gbf.FunctionCoverageRunner):
#           <your implementation here>
#   etc...

## The Mutator and Schedule classes can also be extended or
## replaced by you to create your own fuzzer!

class MyMutator:
    """Mutate strings"""

    def __init__(self) -> None:
        """Constructor"""
        self.mutators = [
            self.delete_random_character,
            self.insert_random_character,
            self.flip_random_character,
            self.reverse_str,
            self.shuffle_str
        ]

class MyMutator(MyMutator):
    def insert_random_character(self, s: str) -> str:
        """Returns s with a random character inserted"""
        pos = random.randint(0, len(s))
        random_character = chr(random.randrange(32, 127))
        return s[:pos] + random_character + s[pos:]

class MyMutator(MyMutator):
    def delete_random_character(self, s: str) -> str:
        """Returns s with a random character deleted"""
        if s == "":
            return self.insert_random_character(s)

        pos = random.randint(0, len(s) - 1)
        return s[:pos] + s[pos + 1:]

class MyMutator(MyMutator):
    def flip_random_character(self, s: str) -> str:
        """Returns s with a random bit flipped in a random position"""
        if s == "":
            return self.insert_random_character(s)

        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 6)
        new_c = chr(ord(c) ^ bit)
        return s[:pos] + new_c + s[pos + 1:]

class MyMutator(MyMutator):
    def reverse_str(self, s: str) -> str:
        return s[::-1]

class MyMutator(MyMutator):
    def shuffle_str(self, s: str) -> str:
        string_list = list(s)
        random.shuffle(string_list)
        shuffled_string = ''.join(string_list)
        return shuffled_string

class MyMutator(MyMutator):
    def mutate(self, inp: object()) -> object():  # can be str or Seed (see below)
        """Return s with a random mutation applied. Can be overloaded in subclasses."""
        # perform more than one random mutations
        for _ in range(random.randint(1, 100)):
            mutator = random.choice(self.mutators)
            inp = mutator(inp)
        return inp

    
# When executed, this program should run your fuzzer for a very 
# large number of iterations. The benchmarking framework will cut 
# off the run after a maximum amount of time
#
# The `get_initial_corpus` and `entrypoint` functions will be provided
# by the benchmarking framework in a file called `bug.py` for each 
# benchmarking run. The framework will track whether or not the bug was
# found by your fuzzer -- no need to keep track of crashing inputs
if __name__ == "__main__":
    seed_inputs = get_initial_corpus()
    fast_schedule = gbf.AFLFastSchedule(5)
    # line_runner = mf.FunctionCoverageRunner(entrypoint)
    line_runner = MyRunner(entrypoint)

    fast_fuzzer = gbf.CountingGreyboxFuzzer(seed_inputs, MyMutator(), fast_schedule)
    fast_fuzzer.runs(line_runner, trials=999999999)
