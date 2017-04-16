import cPickle
import numpy as np
from Config import Config


config = Config('./config/config.conf', False)
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


