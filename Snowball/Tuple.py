
class Tuple():
    def __init__(self, config):
        self.tag1_value = ""
        self.tag2_value = ""
        self.tag1 = config.tag1
        self.tag2 = config.tag2
        
        self.left = dict()
        self.right = dict()
        self.mid = dict()
        
        self.patterns = []
        self.confidence = 0.0
        
        self.is_pos = True 
        