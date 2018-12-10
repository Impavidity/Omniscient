from omniscient.structure import constant

class StageExample(object):

  def __init__(
        self,
        sentence,
        standpoint,
        predicate_positive,
        predicate_positive_direction,
        predicate_negative,
        predicate_negative_direction,
        predicate,
        predicate_direction,
        gold_predicate,
        gold_predicate_direction):
    self.sentence = sentence
    self.standpoint = standpoint
    self.predicate_positive = predicate_positive
    self.predicate_positive_direction = predicate_positive_direction
    self.predicate_negative = predicate_negative
    self.predicate_negative_direction = predicate_negative_direction
    self.predicate = predicate
    self.predicate_direction = predicate_direction
    self.gold_predicate = gold_predicate
    self.gold_predicate_direction = gold_predicate_direction
    self.is_train = True
    if self.predicate != constant.NONE:
      self.is_train = False

  def serialize(self):
    return {
      "sentence": self.sentence.sentence,
      "standpoint": self.standpoint.grounded_value,
      "predicate_positive": self.predicate_positive.value if self.is_train else self.predicate_positive,
      "predicate_positive_direction": self.predicate_positive_direction,
      "predicate_negative": self.predicate_negative["p"] if self.is_train else self.predicate_negative,
      "predicate_negative_direction": self.predicate_negative_direction,
      "predicate": self.predicate if self.is_train else self.predicate["p"],
      "predicate_direction": self.predicate_direction,
      "gold_predicate": self.gold_predicate if self.is_train else self.gold_predicate.value,
      "gold_predicate_direction": self.gold_predicate_direction}

  def __str__(self):
    return str(self.serialize())

  __repr__ = __str__

