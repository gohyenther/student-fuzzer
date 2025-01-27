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
        # implement n-gram coverage
        n = 3
        ngram_coverage = set()
        for i in range(len(self.trace()) - n + 1):
            ngram = tuple(self.trace()[i:i+n])
            ngram_coverage.add(ngram)
        return ngram_coverage


## You can re-implement the runner class to change how
## the fuzzer tracks new behavior in the SUT

class MyRunner(mf.FunctionRunner):

    def run_function(self, inp: str):
        # use own MyCoverage: n-gram coverage implementation
        with MyCoverage() as cov:
            try:
                result = super().run_function(inp)
            except Exception as exc:
                self._coverage = cov.coverage()
                raise exc

        self._coverage = cov.coverage()
        return result

    def coverage(self):
        return self._coverage


## The Mutator and Schedule classes can also be extended or
## replaced by you to create your own fuzzer!

class MyMutator(gbf.Mutator):
    """Mutate strings"""

    def __init__(self) -> None:
        """Constructor"""
        self.mutators = [
            super().delete_random_character,
            super().insert_random_character,
            super().flip_random_character,
            self.toggle_case_alphabets,
            self.swap_random_position
        ]
    
    def toggle_case_alphabets(self, s: str) -> str:
        # Toggle the case (lower or upper case) of a random alphabet in the input s
        if s == "":
            return self.insert_random_character(s)

        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        if ord(c) >= 97 and ord(c) <= 122:
            new_c = chr(ord(c) - 32)
        elif ord(c) >= 65 and ord(c) <= 90:
            new_c = chr(ord(c) + 32)
        else:
            return self.flip_random_character(s)
        return s[:pos] + new_c + s[pos + 1:]
    
    def swap_random_position(self, s: str) -> str:
        # Swap the positions of 2 random characters in the input s
        if s == "":
            return self.insert_random_character(s)

        pos1 = random.randint(0, len(s) - 1)
        c1 = s[pos1]
        pos2 = random.randint(0, len(s) - 1)
        c2 = s[pos2]
        if pos1 > pos2:
            return s[:pos2] + c1 + s[pos2 + 1:pos1] + c2 + s[pos1 + 1:]
        elif pos1 < pos2:
            return s[:pos1] + c2 + s[pos1 + 1:pos2] + c1 + s[pos2 + 1:]
        else:
            return self.flip_random_character(s)
    
    def mutate(self, inp: object()) -> object():  # can be str or Seed (see below)
        # Return s with a random mutation applied. Can be overloaded in subclasses.
        mutator = random.choice(self.mutators)
        return mutator(inp)

    
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
    line_runner = MyRunner(entrypoint)

    fast_fuzzer = gbf.CountingGreyboxFuzzer(seed_inputs, gbf.Mutator(), fast_schedule)
    fast_fuzzer.runs(line_runner, trials=999999999)
