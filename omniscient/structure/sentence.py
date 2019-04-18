from copy import deepcopy

class Sentence(object):
  """
  Sentence

  Attributes:

  """
  def __init__(
        self,
        sentence,
        tokenizer=None):
    """

    Args:
      sentence (str): The full sentence in a string
      tokenizer (callable): If not explicit tokenizer is provided,
        default space tokenizer will used
    """
    self.sentence = sentence
    self.tokenizer = tokenizer
    if tokenizer:
      self.tokens = tokenizer(self.sentence)
    else:
      self.tokens = self.sentence.strip().split()
    self.mentions = {}

  def add_mention(self, mention):
    if mention.span not in self.mentions:
      self.mentions[mention.span] = mention
    else:
      for linked_data in mention.linked_data_list:
        self.mentions[mention.span].add_linked_data(deepcopy(linked_data))
      del mention

  def to_masked_string(self):
    labels = ['O'] * len(self.tokens)
    for span in self.mentions:
      start = True
      for i in range(span[0], span[1]):
        if start:
          labels[i] = 'B'
          start = False
        else:
          labels[i] = 'I'
    masked = []
    start = False
    for token, label in zip(self.tokens, labels):
      if label == 'O':
        if start:
          masked.append('<mask>')
        masked.append(token)
      elif label == 'I':
        continue
      elif label == 'B':
        masked.append('<mask>')
    if start:
      masked.append('<mask>')
    return " ".join(masked)

  def __len__(self):
    return len(self.tokens)

  def __str__(self):
    return " ".join(self.tokens)