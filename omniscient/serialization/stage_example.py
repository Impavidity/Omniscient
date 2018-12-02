from omniscient.structure import constant

class StageExample(object):

  def __init__(
        self,
        sentence,
        predicate_positive,
        predicate_negative,
        predicate,
        gold_predicate):
    self.sentence = sentence
    self.predicate_positive = predicate_positive
    self.predicate_negative = predicate_negative
    self.predicate = predicate
    self.gold_predicate = gold_predicate
    self.is_train = True
    if self.predicate != constant.NONE:
      self.is_train = False

  def serialize(self):
    return {
      "sentence": self.sentence.sentence,
      "predicate_positive": self.predicate_positive.value if self.is_train else self.predicate_positive,
      "predicate_negative": self.predicate_negative["p"] if self.is_train else self.predicate_negative,
      "predicate": self.predicate if self.is_train else self.predicate["p"],
      "gold_predicate": self.gold_predicate if self.is_train else self.gold_predicate.value}

  def __str__(self):
    return str(self.serialize())

  __repr__ = __str__

