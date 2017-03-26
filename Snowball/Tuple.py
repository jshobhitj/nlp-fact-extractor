
class Tuple():
    def __init__(self, config, tag1_value, tag2_value):
        self.tag1_value = tag1_value
        self.tag2_value = tag2_value
        self.tag1 = config.tag1
        self.tag2 = config.tag2
        
        self.left = dict()
        self.right = dict()
        self.mid = dict()
        
        self.patterns = []
        self.confidence = 0.0
        
        self.is_pos = True
        
    def __repr__(self):
        return self.tag1 + " : " + self.tag1_value + ", " + self.tag2 + " : " + self.tag2_value