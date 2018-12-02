class Mention(object):
  def __init__(
        self,
        start=None,
        end=None,
        mention_text=None,
        linked_uri=None):
    self.start = start
    self.end = end
    self.mention_text = mention_text
    self.linked_uri = linked_uri