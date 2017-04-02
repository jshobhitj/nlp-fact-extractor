from Pattern import Pattern
from Tuple import Tuple
from ProcessedTuples import ProcessedTuples
from Config import Config
import pickle
import os

class Snowball:
    def __init__(self):
        self.config = Config(r"./config/config.conf")
        self.patterns = []
        self.seed_tuples = []
        self.candidate_tuples = []
        
        self.initialize_seed()
        
    def initialize_seed(self):
        seed_file = open(self.config.seeds_file, 'r')
        for line in seed_file:
            words = [x.strip() for x in line.split('=')]
            t = Tuple(self.config, words[0], words[1])
            t.conf = 1.0
            self.seed_tuples.append(t)

    def run_snowball(self):
        for iter in range(self.config.max_iterations):
            matches = self.find_matches()
            
            self.cluster_matches(matches)
            
            self.filter_patterns()
            
            self.generate_tuples()

            self.update_pattern_confidence()

            self.update_tuple_confidence()
            
            self.add_seed_tuples()
        
    def find_matches(self):
        # TODO: Remove tuples with period (.) in processed tuples
        # TODO: Case-folding for processed tuples
        matches = []

        #if processed tuples file is not present, generate tuples
        if not os.path.isfile(self.config.processed_tuples_file):
            self.config.generate_processed_tuples()
        
        # Read the data
        for p_tuple in ProcessedTuples(self.config):
            for s_tuple in self.seed_tuples:
                if p_tuple != s_tuple:
                    continue
                else:
                    matches.append(p_tuple)
                    break
        return matches

    def cluster_matches(self, matches):
        for m_tuple in matches:
            is_match_found = False
            for pattern in self.patterns:
                similarity = pattern.get_match_score(m_tuple)
                if similarity >= self.config.sim_threshold:
                    is_match_found = True
                    pattern.update_centroid(m_tuple)

            if is_match_found is False:
                new_pattern = Pattern(self.config)
                new_pattern.update_centroid(m_tuple)
                self.patterns.append(new_pattern)
        
    def filter_patterns(self):
        for pattern in self.patterns:
            if len(pattern.supp_seed_tuples) >= self.config.support_threshold:
                pattern.match_count = 1
            else:
                self.patterns.remove(pattern)
        
    def generate_tuples(self):
        for p_tuple in ProcessedTuples(self.config):
            best_similarity = 0.0
            best_pattern = None
            for pattern in self.patterns:
                similarity = pattern.get_match_score(p_tuple)
                if similarity >= self.config.sim_threshold:
                    pattern.update_selectivity(self.seed_tuples, p_tuple)

                    if similarity >= best_similarity:
                        best_similarity = similarity
                        best_pattern = pattern

            if best_similarity >= self.config.sim_threshold:
                p_tuple.gen_patterns.append({best_pattern: best_similarity})
                # TODO: Should we check for the tuple that is already in candidate tuples list from previous iteration
                self.candidate_tuples.append(p_tuple)

    def normalize_conf(self, entries, norm_factor):
        for entry in entries:
            entry.conf /= norm_factor

    def update_pattern_confidence(self):
        max_conf = 0.0
        for pattern in self.patterns:
            pattern.update_confidence()
            if pattern.conf > max_conf:
                max_conf = pattern.conf

        self.normalize_conf(self.patterns, max_conf)

    def update_tuple_confidence(self):
        max_conf = 0.0
        for t in self.candidate_tuples:
            t.update_tuple_confidence()
            if t.conf > max_conf:
                max_conf = t.conf

        self.normalize_conf(self.candidate_tuples, max_conf)

    def add_seed_tuples(self):
        # TODO: Need to check whether candidate tuple is already in seed or
        # TODO: not if it is then whether to update conf or not
        for t in self.candidate_tuples:
            if t.conf >= self.config.tuple_conf_threshold:
                self.seed_tuples.append(t)


def main():
    snowball = Snowball()
    snowball.run_snowball()

    # Evaluation
    # print results
        
if __name__ == "__main__":
    main()
