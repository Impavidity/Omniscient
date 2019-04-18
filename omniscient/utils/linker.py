import re
import logging
import pkg_resources

from omniscient.structure.linked_data import (
  LinkedData)
from omniscient.structure.mention import Mention


logging.getLogger().setLevel(logging.INFO)

ORDINAL_VOCAB_FILE_PATH = pkg_resources.resource_filename('omniscient', 'resource/lexical/ordinal_lexical.tsv')

class Linker(object):
  """

  """

  def __init__(
        self,
        ordinal_vocab_file_path=ORDINAL_VOCAB_FILE_PATH):
    self.year_re = re.compile(r'^[1-2][0-9][0-9][0-9]$')
    """Regular Expression for extracting year"""
    self.ordinal_word_dict = {}
    self.superlative_words = set([])

    with open(ordinal_vocab_file_path, 'r') as fin:
      for line in fin.readlines():
        spt = line.strip().split(' ')
        if spt[0] in ('max', 'min'):
          self.superlative_words |= set(spt[1].split(','))
        else:
          num = int(spt[0])
          for wd in spt[1].split(','):
            self.ordinal_word_dict[wd] = num
            self.superlative_words.add(wd)
    logging.info(' {} ordinal & {} superlative words loaded.'.format(
                 len(self.ordinal_word_dict), len(self.superlative_words)))

  def entity_linking(self, sentence):
    """
    This entity linking function is doing linking from scratch
    Currently we do not have good implementation for this.
    Basically we would like to replace this function with any
      complicated model, with a lot of feature engineer, with
      lexical dictionary etc.
    Args:
      sentence (Sentence):

    """
    pass


  def time_linking(self, sentence):
    """
    We use regular expression to extract year from sentence
    In this function, you will create a Mention object, pointing to list of LinkedData
    Process:

    Args:
      sentence (Sentence)

    Returns:
      List(LinkedData)

    """
    for idx, token in enumerate(sentence.tokens):
      if re.match(self.year_re, token[:4]):
        year = token[:4]
        last_token = sentence.tokens[idx - 1] if idx > 0 else ''
        comp = "=="
        if last_token == "before":
          comp = "<"
        elif last_token == "after":
          comp = ">"
        elif last_token == "since":
          comp = ">="
        st = idx
        end = idx + 1
        mention = Mention(
          start=st,
          end=end,
          mention_text=" ".join(sentence.tokens[st: end]))
        mention.add_linked_data(LinkedData(
          category=LinkedData.TIME,
          comp=comp,
          value=year,
          label='', # TODO: distinguish these
          linking_feature=None))
        sentence.add_mention(mention=mention)



  def ordinal_linking(self, sentence):
    """
    Extract ordinal information
    In this scripts, we consider 3 cases:
      - Single xx-th word: first, 4th, most, least
      - Single -est word: longest, largest
      - xx-th -est combination: second largest

    Args:
      sentence (Sentence): List of tokens

    Returns:
      List(`LinkedData`)
    """
    token_size = len(sentence)
    for idx in range(token_size):
      token = sentence.tokens[idx]
      if token in self.superlative_words:
        """Find a superlative word"""
        if idx + 1 < token_size and sentence.tokens[idx + 1] in self.superlative_words:
          """We will examine superlative phrase together
             and start for the last token of the phrase"""
          continue
        if idx > 0 and sentence.tokens[idx - 1] in self.ordinal_word_dict:
          """xx-th xx-est combination"""
          st = idx - 1
          num = self.ordinal_word_dict[sentence.tokens[idx - 1]]
          """Extract the direct ordinal number"""
        else:
          st = idx
          if token in self.ordinal_word_dict:
            """Single xx-th"""
            num = self.ordinal_word_dict[token]
          else:
            """Single xx-est, default rank = 1"""
            num = 1
        end = idx + 1
        mention = Mention(
          start=st,
          end=end,
          mention_text=" ".join(sentence.tokens[st: end]))
        for comp in ('max', 'min'):
          """Consider both directions"""
          mention.add_linked_data(
            LinkedData(
              category=LinkedData.ORDINAL,
              comp=comp,
              value=str(num),
              label='',
              linking_feature=None))
        sentence.add_mention(mention=mention)



if __name__ == "__main__":
  from omniscient.structure.sentence import Sentence
  linker = Linker()
  sentence = Sentence("What is the longest river in the world ?")
  print(sentence)
  linker.ordinal_linking(sentence=sentence)
  for span in sentence.mentions:
    print(sentence.mentions[span])
  sentence = Sentence("Who is the president of US in 1997")
  print(sentence)
  linker.time_linking(sentence)
  for span in sentence.mentions:
    print(sentence.mentions[span])