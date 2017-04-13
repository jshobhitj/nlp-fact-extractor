
class Tuple:
    def __init__(self, config, tag1_value, tag2_value, left_dict = dict(), mid_dict = dict(), right_dict = dict()):
        self.config = config
        self.tag1_value = tag1_value
        self.tag2_value = tag2_value
        self.tag1 = config.tag1  # ORGANIZATION
        self.tag2 = config.tag2  # LOCATION
        
        self.left = left_dict
        self.mid = mid_dict
        self.right = right_dict

        # List of patterns which helped
        # generating this tuple.
        self.gen_patterns = {}
        self.conf = 0.0
        
        self.is_pos = True
        
    def __repr__(self):
        return self.tag1 + " : " + self.tag1_value.encode('ascii', 'ignore') + ", " \
               + self.tag2 + " : " + self.tag2_value.encode('ascii', 'ignore') + ", Conf: " + str(self.conf)

    def __eq__(self, other):
        if other is None:
            return False
        return self.tag1_value == other.tag1_value and self.tag2_value == other.tag2_value

    def __ne__(self, other):
        if other is None:
            return True
        return self.tag1_value != other.tag1_value or self.tag2_value != other.tag2_value

    def update_tuple_confidence(self):
        new_conf = 1.0
        for pattern, similarity in self.gen_patterns.items():
            new_conf *= (1 - (pattern.conf * similarity))
        self.conf = 1 - new_conf
