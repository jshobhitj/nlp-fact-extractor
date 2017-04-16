import os
import math
import string
import cPickle
import ConfigParser

from Tuple import Tuple
from collections import defaultdict


class Config:
    def __init__(self, config_file_path, generate_tuples=True):
        self.config_file_path = config_file_path

        configParser = ConfigParser.RawConfigParser()
        configParser.read(config_file_path)

        self.training_folder = configParser.get('Config', 'training_folder')
        self.testing_file = configParser.get('Config', 'testing_file')
        self.seeds_file = configParser.get('Config', 'seeds_file')
        self.fact_file = configParser.get('Config', 'fact_file')
        self.valid_locations_file = configParser.get('Config', 'valid_locations_file')
        self.processed_tuples = []
        
        self.sim_threshold = float(configParser.get('Config', 'sim_threshold'))
        self.tuple_conf_threshold = float(configParser.get('Config', 'tuple_conf_threshold'))
        self.support_threshold = float(configParser.get('Config', 'support_threshold'))

        self.max_iterations = int(configParser.get('Config', 'max_iterations'))
        self.middle_wt = float(configParser.get('Config', 'middle_wt'))
        self.left_wt = float(configParser.get('Config', 'left_wt'))
        self.right_wt = float(configParser.get('Config', 'right_wt'))
        self.window_size = int(configParser.get('Config', 'window_size'))
        self.left_limit = int(configParser.get('Config', 'left_limit'))
        self.right_limit = int(configParser.get('Config', 'right_limit'))

        self.weight_update = float(configParser.get('Config', 'weight_update'))

        self.min_freq_for_token = float(configParser.get('Config', 'min_freq_for_token'))
        
        self.tag1 = configParser.get('Config', 'tag1')
        self.tag2 = configParser.get('Config', 'tag2')

        # if processed tuples file is not present, generate tuples
        # if not os.path.isfile(self.processed_tuples_file):
        if generate_tuples:
            self.generate_processed_tuples()
        
    def __repr__(self):
        pass
    
    def norm(self, d):
        magnitude = 0
        for i in d:
            magnitude += d[i] * d[i]
        for i in d:
            d[i] /= float(math.sqrt(magnitude))

    #generate processed tuples from tagged training directory files
    def generate_processed_tuples(self):
        count = 0

        tokens = defaultdict(int)
        locations = self.get_valid_loc()
        for subdir, dirs, files in os.walk(self.training_folder):
            for file in files:
                path = os.path.join(subdir, file)
                f = open(path, 'r')
                while True:
                    try:
                        tagged_line = cPickle.load(f)
                    except EOFError:
                        print "\nTotal Processed Tuples: " + str(len(self.processed_tuples))
                        break

                    final_tagged_line = self.process_tagged_line(tagged_line)

                    # print(final_tagged_line)

                    # find org-loc pairs in final tagged line
                    for idx in range(len(final_tagged_line)):
                        if (final_tagged_line[idx][1] == self.tag1):
                            idx_org = idx
                            idx_loc = -1

                            for idx_2 in range(idx_org + 1, idx_org + self.window_size + 1):
                                if (idx_2 >= len(final_tagged_line)): break

                                if (final_tagged_line[idx_2][1] == self.tag2):
                                    idx_loc = idx_2; break
                                elif (final_tagged_line[idx_2][1] == self.tag1): break;

                            if idx_loc != -1:
                                #build left, middle and right contexts
                                left_dict = defaultdict(int); mid_dict = defaultdict(int); right_dict = defaultdict(int);
                                i = idx_org - 1
                                while (i >= 0 and i >= (idx_org - self.left_limit) and final_tagged_line[i][1] != self.tag1 and final_tagged_line[i][1] != self.tag2):
                                    left_dict[final_tagged_line[i][0]] = 1
                                    tokens[final_tagged_line[i][0]] += 1
                                    i -= 1

                                i = idx_org + 1
                                while (i < idx_loc and final_tagged_line[i][1] != self.tag1 and final_tagged_line[i][1] != self.tag2):
                                    mid_dict[final_tagged_line[i][0]] = 1
                                    tokens[final_tagged_line[i][0]] += 1
                                    i += 1

                                i = idx_loc + 1
                                while (i < len(final_tagged_line) and i < (idx_loc + self.right_limit + 1) and final_tagged_line[i][1] != self.tag1 and final_tagged_line[i][1] != self.tag2):
                                    right_dict[final_tagged_line[i][0]] = 1
                                    tokens[final_tagged_line[i][0]] += 1
                                    i += 1

                                # print(left_dict)
                                # print(mid_dict)
                                # print(right_dict)

                                # Ignore invalid locations
                                if self.check_valid_location(locations, final_tagged_line[idx_loc][0].encode('ascii', 'ignore')) is False:
                                    continue
                                print(final_tagged_line[idx_org][0], final_tagged_line[idx_loc][0])
                                t = Tuple(self, final_tagged_line[idx_org][0], final_tagged_line[idx_loc][0], left_dict, mid_dict, right_dict)
                                self.processed_tuples.append(t)

        self.modify_word_vector(tokens)

    def modify_word_vector(self, tokens):
        for pt in self.processed_tuples:
            for word in pt.left.keys():
                val = math.log(tokens[word], 2)
                if val > self.min_freq_for_token:
                    pt.left[word] = val
                else:
                    del pt.left[word]
            self.norm(pt.left)
            for word in pt.mid.keys():
                val = math.log(tokens[word], 2)
                if val > self.min_freq_for_token:
                    pt.mid[word] = val
                else:
                    del pt.mid[word]
            self.norm(pt.mid)
            for word in pt.right.keys():
                val = math.log(tokens[word], 2)
                if val > self.min_freq_for_token:
                    pt.right[word] = val
                else:
                    del pt.right[word]
            self.norm(pt.right)

    def check_valid_location(self, locations, loc):
        loc = loc.translate(None, string.punctuation).lower()
        return loc in locations

    def get_valid_loc(self):
        locations = set(['united states of america', 'us', 'usa', 'united states', 'u s a', 'u s', 'n y'])
        f = open(self.valid_locations_file, 'r')
        idx = -1
        for line in f:
            idx += 1
            if idx == 0:
                continue
            line = line[:-1]
            locs = line.split('|')
            for loc in locs:
                loc = loc.translate(None, string.punctuation).lower()
                locations.add(loc)
        f.close()
        return locations

    # join split ORGANIZATION LOCATION tags and separate punctuations
    def process_tagged_line(self, tagged_line):
        idx = 0; final_tagged_line = []
        
        while idx in range(len(tagged_line)):
            if tagged_line[idx][1] != self.tag1 and tagged_line[idx][1] != self.tag2:
                #use word_tokenize to separate punctuations(comma and periods)
                # processed_tokens = word_tokenize(tagged_line[idx][0])

                final_tagged_line += [tagged_line[idx]]
                idx += 1
            
            org = ''; first = True
            while (idx < len(tagged_line) and tagged_line[idx][1] == self.tag1):
                if (not first): org += ' '
                org += tagged_line[idx][0]
                idx += 1; first = False
                
            if (org != ''):
                comma_present = False
                if (org[-1:] == ','):
                    org = org[:-1]
                    comma_present = True
                final_tagged_line += [(org, self.tag1)];
                if comma_present:
                    final_tagged_line += [(',', 'O')]
                
            loc = ''
            first = True
            while (idx < len(tagged_line) and tagged_line[idx][1] == self.tag2):
                if (not first): loc += ' '
                loc += tagged_line[idx][0]; 
                idx += 1; first = False
                
            if (loc != ''):
                #TODO: handle case when LOCATION ends with period not comma ( Menlo Park.)
                comma_present = False
                if (loc[-1:] == ','):
                    loc = loc[:-1]
                    comma_present = True
                final_tagged_line += [(loc, self.tag2)];
                if comma_present:
                    final_tagged_line += [(',', 'O')]
        
        return final_tagged_line
