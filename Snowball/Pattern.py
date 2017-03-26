
class Pattern(object):
    def __init__(self, config):
        #organization
        self.tag1 = config.tag1
        self.tag2 = config.tag2
        self.left_centroid = dict()
        self.right_centroid = dict()
        self.mid_centroid = dict()
        self.conf = 0.0
        self.supp_tuple_count = 0 
        self.conf_rlog_f = 0.0 
        self.pos_count = 0
        self.neg_count = 0