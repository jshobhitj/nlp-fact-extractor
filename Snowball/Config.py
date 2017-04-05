import ConfigParser
import cPickle
from collections import defaultdict
from Tuple import Tuple
import math
import os


class Config:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

        configParser = ConfigParser.RawConfigParser()
        configParser.read(config_file_path)
        
        self.training_dir = configParser.get('Config', 'training_dir')
        self.testing_file = configParser.get('Config', 'testing_file')
        self.seeds_file = configParser.get('Config', 'seeds_file')
        self.processed_tuples_file = configParser.get('Config', 'processed_tuples_file')
        self.processed_tuples = []
        
        self.sim_threshold = float(configParser.get('Config', 'sim_threshold'))
        self.tuple_conf_threshold = float(configParser.get('Config', 'tuple_conf_threshold'))
        self.support_threshold = float(configParser.get('Config', 'support_threshold'))

        self.max_iterations = int(configParser.get('Config', 'max_iterations'))
        self.middle_wt = float(configParser.get('Config', 'middle_wt'))
        self.left_wt = float(configParser.get('Config', 'left_wt'))
        self.right_wt = float(configParser.get('Config', 'right_wt'))
        self.window_size = int(configParser.get('Config', 'window_size'))

        self.weight_update = float(configParser.get('Config', 'weight_update'))
        
        self.tag1 = configParser.get('Config', 'tag1')
        self.tag2 = configParser.get('Config', 'tag2')

        # if processed tuples file is not present, generate tuples
        # if not os.path.isfile(self.processed_tuples_file):
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
        
        #TODO: tagged files need to be picked from training_dir 
        # with open('./data/AA/wiki_02', 'rb') as f:
        data = './data/AA/'
        for subdir, dirs, files in os.walk(data):
            for file in files:
                f = open(data + file, 'r')
                while True:
                    try:
                        tagged_line = cPickle.load(f)
                    except EOFError:
                        print "\nTotal Processed Tuples: " + str(len(self.processed_tuples))
                        break

                    # count += 1
                    # if (count != 12): continue

                    final_tagged_line = self.process_tagged_line(tagged_line)
                    # final_tagged_line = tagged_line

                    # print('final tagged_line')
                    # print(final_tagged_line)
                    tag_matches = []

                    #find org-loc pairs in final tagged line
                    for idx in range(len(final_tagged_line)):
                        if (final_tagged_line[idx][1] == self.tag1):
                            idx_org = idx
                            idx_loc = -1

                            for idx_2 in range(idx_org + 1, idx_org + self.window_size + 1):
                                if (idx_2 >= len(final_tagged_line)): break

                                if (final_tagged_line[idx_2][1] == self.tag2):
                                    idx_loc = idx_2; break;
                                elif (final_tagged_line[idx_2][1] == self.tag1): break;

                            if (idx_loc != -1):

                                #build left, middle and right contexts
                                left_dict = defaultdict(int); mid_dict = defaultdict(int); right_dict = defaultdict(int);
                                i = idx_org - 1
                                while (i >= 0 and i >= (idx_org - self.window_size) and final_tagged_line[i][1] != self.tag1 and final_tagged_line[i][1] != self.tag2):
                                    left_dict[final_tagged_line[i][0]] += 1
                                    i -= 1
                                self.norm(left_dict)

                                i = idx_org + 1
                                while (i < idx_loc and final_tagged_line[i][1] != self.tag1 and final_tagged_line[i][1] != self.tag2):
                                    mid_dict[final_tagged_line[i][0]] += 1
                                    i += 1
                                self.norm(mid_dict)

                                i = idx_loc + 1
                                while (i < len(final_tagged_line) and i < (idx_loc + self.window_size + 1) and final_tagged_line[i][1] != self.tag1 and final_tagged_line[i][1] != self.tag2):
                                    right_dict[final_tagged_line[i][0]] += 1
                                    i += 1
                                self.norm(right_dict)

                                # print(left_dict)
                                # print(mid_dict)
                                # print(right_dict)
                                print(final_tagged_line[idx_org][0], final_tagged_line[idx_loc][0])
                                t = Tuple(self, final_tagged_line[idx_org][0], final_tagged_line[idx_loc][0], left_dict, mid_dict, right_dict)
                                self.processed_tuples.append(t)
                    # print(tag_matches)

                    # write matches to file
                    # print(self.processed_tuples_file)
                    # tuple_file = open(self.processed_tuples_file, "w")
                    # for pt in self.processed_tuples:
                    #    cPickle.dump(pt, tuple_file)

    # join split ORGANIZATION LOCATION tags and separate punctuations
    def process_tagged_line(self, tagged_line):
        idx = 0; final_tagged_line = []
        
        while idx in range(len(tagged_line)):
            if tagged_line[idx][1] != self.tag1 and tagged_line[idx][1] != self.tag2:
                #use word_tokenize to separate punctuations(comma and periods)
                # processed_tokens = word_tokenize(tagged_line[idx][0])

                final_tagged_line += [tagged_line[idx]];
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
                    
                
            loc = ''; first = True
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
                        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        