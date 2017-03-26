from numpy.compat.setup import configuration
import sys
from Pattern import Pattern
from Tuple import Tuple
from Config import Config
import ast

class Snowball(object):    
    def __init__(self):
        self.config = Config(r"./config/config.conf")
        self.patterns = []
        self.seed_tuples = []
        self.cand_tuples = []
        
        self.initialize_seed()
        
    def initialize_seed(self):
        seed_file = open(self.config.seeds_file, 'r')
        for line in seed_file:
            words = [x.strip() for x in line.split('=')]
            self.seed_tuples.append(Tuple(self.config, words[0], words[1]))
        
#         print("seed tuples: ")
#         print(self.seed_tuples)


    def run_snowball(self):
        for iter in range(self.config.max_iterations):
            matches = self.find_matches()
            
            self.cluster_patterns()
            
            self.filter_patterns()
            
            self.generate_tuples()
            
            self.filter_tuples()
        
    def find_matches(self):
            pass
        
    def cluster_patterns(self):
        pass
        
    def filter_patterns(self):
        pass
        
    def generate_tuples(self):
        pass
        
    def filter_tuples(self):
        pass

def main():
    snowball = Snowball()
        
if __name__ == "__main__":
    main()
