import ConfigParser


class Config:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

        configParser = ConfigParser.RawConfigParser()
        configParser.read(config_file_path)
        
        self.training_dir = configParser.get('Config', 'training_dir')
        self.testing_file = configParser.get('Config', 'testing_file')
        self.seeds_file = configParser.get('Config', 'seeds_file')
        self.processed_tuples = configParser.get('Config', 'processed_tuples_file')
        
        self.sim_threshold = float(configParser.get('Config', 'sim_threshold'))
        self.tuple_conf_threshold = float(configParser.get('Config', 'tuple_conf_threshold'))
        self.support_threshold = float(configParser.get('Config', 'support_threshold'))

        self.max_iterations = float(configParser.get('Config', 'max_iterations'))
        self.middle_wt = float(configParser.get('Config', 'middle_wt'))
        self.left_wt = float(configParser.get('Config', 'left_wt'))
        self.right_wt = float(configParser.get('Config', 'right_wt'))
        self.window_size = float(configParser.get('Config', 'window_size'))
        self.weight_update = float(configParser.get('Config', 'weight_update'))
        
        self.tag1 = configParser.get('Config', 'tag1')
        self.tag2 = configParser.get('Config', 'tag2')
        
    def __repr__(self):
        pass
        
        
        
        
        