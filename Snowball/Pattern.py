import copy
import math


class Pattern:
    def __init__(self, config):
        self.config = config

        self.tag1 = config.tag1  # ORGANIZATION
        self.tag2 = config.tag2  # LOCATION

        self.left_centroid = dict()
        self.mid_centroid = dict()
        self.right_centroid = dict()

        self.conf = 0.0

        self.supp_seed_tuples = set()
        self.match_count = 0

        self.pos_count = 0.0
        self.neg_count = 0.0

    # This method computes the dot product of two vectors
    # v1 (pattern's left/middle/right vector) and
    # v2 (tuple's) left/middle/right vector)
    def get_dot_product(self, v1, v2):
        total_val = 0.0
        for token1, val1 in v1.items():
            val2 = v2.get(token1)
            if val2 is None:
                continue
            else:
                total_val += (val1 * val2)
        return total_val

    def get_match_score(self, t):
        score = 0.0
        score += self.config.left_wt * self.get_dot_product(self.left_centroid, t.left)
        score += self.config.middle_wt * self.get_dot_product(self.mid_centroid, t.mid)
        score += self.config.right_wt * self.get_dot_product(self.right_centroid, t.right)
        return score

    def normalize(self, v):
        sq_sum = 0.0
        for val in v.values():
            sq_sum += (val * val)
        mag = math.sqrt(sq_sum)
        for token, val in v.items():
            val /= mag
            v.update({token: val})

    # This method updates the centroid of pattern
    # v1 (pattern's left/middle/right vector) and
    # v2 (tuple's) left/middle/right vector)
    def update(self, v1, v2):
        union = dict(v1, **v2)
        for token in union.keys():
            val1 = v1.get(token)
            val2 = v2.get(token)
            if val1 is None:
                val1 = val2 / (self.match_count + 1)
            else:
                val1 *= self.match_count
                if val2 is not None:
                    val1 += val2
                val1 /= (self.match_count + 1)
            v1.update({token: val1})

    def update_centroid(self, t):
        if self.match_count == 0:
            self.left_centroid = copy.deepcopy(t.left)
            self.mid_centroid = copy.deepcopy(t.mid)
            self.right_centroid = copy.deepcopy(t.right)
        else:
            self.update(self.left_centroid, t.left)
            self.normalize(self.left_centroid)

            self.update(self.mid_centroid, t.mid)
            self.normalize(self.mid_centroid)

            self.update(self.right_centroid, t.right)
            self.normalize(self.right_centroid)
        self.match_count += 1
        self.supp_seed_tuples.add((t.tag1_value, t.tag2_value))

    def update_selectivity(self, seed_tuples, t):
        is_already_in_seed = False
        for s_tuple in seed_tuples:
            if s_tuple == t:
                self.pos_count += 1
                is_already_in_seed = True
            elif s_tuple.tag1_value == t.tag1_value:
                t.is_pos = False
                self.neg_count += 1

        # TODO: Whether to consider tuples from current iteration in this calculation or not
        if is_already_in_seed is False:
            self.pos_count += 1

    def update_confidence(self):
        new_conf = self.pos_count / (self.pos_count + self.neg_count)
        new_conf_rlog_f = new_conf * math.log(self.pos_count, 2)
        self.conf *= (1 - self.config.weight_update)
        self.conf += (new_conf_rlog_f * self.config.weight_update)
