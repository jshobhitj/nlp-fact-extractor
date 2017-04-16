import cPickle
import numpy as np
from Config import Config
from collections import defaultdict


config = Config('./config/config.conf')
f = open(config.testing_file, 'r')
companies = None
while True:
    try:
        companies = cPickle.load(f)
    except EOFError:
        break

facts_file = open(config.fact_file, 'w')
for index in range(100):
    st = '{"' + config.tag1 + '" : "' + np.random.choice(companies, replace=False) + '", "' + config.tag2 + '" : []}\n'
    facts_file.write(st)

test = defaultdict(lambda: [])
companies = set(companies)
for t in config.processed_tuples:
    if t.tag1_value in companies:
        test[t.tag1_value] += [t.tag2_value]

print "\nCompanies Total Count: " + str(len(companies))
print "List entry count: " + str(len(test))
for c, l in test.items():
    print "ORG: " + c + " GPE: " + str(l)

