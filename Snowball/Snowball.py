import re
import json
import nltk
import cPickle

from Pattern import Pattern
from Tuple import Tuple
from Config import Config
from collections import defaultdict


# nltk.download('stopwords')


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
            fact = json.loads(line)
            tag_a = fact[self.config.tag1]
            tag_b = fact[self.config.tag2]
            t = Tuple(self.config, tag_a, tag_b)
            t.conf = 1.0
            self.seed_tuples.append(t)

    def run_snowball(self):
        for iter in range(self.config.max_iterations):
            print "\nIter: " + str(iter)
            print "Seed size: " + str(len(self.seed_tuples))
            print sorted(self.seed_tuples, key=lambda tuple: tuple.conf, reverse=True)

            matches = self.find_matches()
            print "Matches: " + str(len(matches))
            print matches
            
            self.cluster_matches(matches)
            
            self.filter_patterns()
            
            self.generate_tuples()

            self.update_pattern_confidence()

            self.update_tuple_confidence()
            
            self.add_seed_tuples()
            # print "\nPatterns: "
            # print self.patterns

        self.add_seed_tuples()
        # print "\nPatterns: "
        # print self.patterns
        print "\nFinal Seed size: " + str(len(self.seed_tuples))
        print sorted(self.seed_tuples, key=lambda tuple: tuple.conf, reverse=True)
        
        print "\nEvaluation: "
        self.test()
        # self.evaluation()
        
    def find_matches(self):
        matches = []
        
        # Read the data
        # for p_tuple in ProcessedTuples(self.config):
        for p_tuple in self.config.processed_tuples:
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
        # for p_tuple in ProcessedTuples(self.config):
        for p_tuple in self.config.processed_tuples:
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
                p_tuple.gen_patterns.update({best_pattern: best_similarity})
                # TODO: Should we check for the tuple that is already in candidate tuples list from previous iteration
                self.candidate_tuples.append(p_tuple)

    def normalize_conf(self, entries, norm_factor):
        if norm_factor == 0:
            return
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
        for t in self.candidate_tuples:
            if t.conf >= self.config.tuple_conf_threshold and t.is_pos:
                is_not_in_seed = True
                idx = -1
                for s_tuple in self.seed_tuples:
                    idx += 1
                    if s_tuple == t:
                        is_not_in_seed = False
                        break
                    elif s_tuple.tag1_value == t.tag1_value:
                        if t.conf > s_tuple.conf:
                            s_tuple.is_pos = False
                            del self.seed_tuples[idx]
                        else:
                            is_not_in_seed = False
                            t.is_pos = False
                        break

                if is_not_in_seed:
                    self.seed_tuples.append(t)

    def test(self):
        f = open(self.config.testing_file, 'r')
        companies = None
        while True:
            try:
                companies = cPickle.load(f)
            except EOFError:
                break

        companies = set(companies)
        #companies_base = [company.replace(" ", "") for company in companies] 
        
        idx = 0
        for seed in self.seed_tuples:
            st = seed.tag1_value
            st = re.sub('[t|T]he\s+', '', st)
            if st in companies:
                print seed
                idx += 1

        print '\n'
        print 'Count: ' + str(idx)
        print 'Total Companies: ' + str(len(companies))
        print '\n'
                
    def evaluation(self):
        #assume facts is in json format
        facts = open(self.config.fact_file, 'r')
        ideal_dict = defaultdict(lambda: list)
        join_set = set()
        tag1_type = self.config.tag1
        tag2_type = self.config.tag2
        
        for line in facts:
            fact = json.loads(line)
            #store canonical form of org name in ideal_dict, i.e. only first word and lower case alphanum
            ideal_dict[self.canonical_org(fact[tag1_type])] = fact[tag2_type]
        
        true_pos = 0
        #calculate join_dict
        for tup in self.seed_tuples[0:4]:
            base_org = self.canonical_org(tup.tag1_value) 
            print('\nbase_org: ', base_org)
            if base_org in ideal_dict:
                join_set.add(base_org)
                
                for ideal_loc_val in ideal_dict[base_org]:
                    print('matching: ', tup.tag2_value, ideal_loc_val) 
                    if (self.is_loc_equal(tup.tag2_value, ideal_loc_val)):
                        true_pos += 1
        
        print('true_pos: ', true_pos)
        print('\nideal_dict: ', ideal_dict)
        print('\njoin_set: ', join_set)
        
        #calculate precision
        precision = true_pos / float(len(join_set)) 
        
        #calculate recall
        recall = true_pos / float(len(ideal_dict))
        
        print("precision: ", precision)
        print("recall: ", recall)
    
    def canonical_org(self, org):
        stop_list = nltk.corpus.stopwords.words("english")
        org_names = [word for word in org.split() if word not in stop_list]
        org_head = org_names[0]
        
        return re.sub('\W+', '', org_head).lower()
    
    def is_loc_equal(self, loc1, loc2):
        return re.sub('\W+', '', loc1).lower() == re.sub('\W+', '', loc2).lower()


def main():
    snowball = Snowball()
    snowball.run_snowball()
        
if __name__ == "__main__":
    main()
