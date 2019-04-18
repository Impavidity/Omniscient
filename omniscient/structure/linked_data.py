class LinkedData(object):

  ENTITY = "Entity"
  TYPE = "Type"
  TIME = "Time"
  ORDINAL = "Ordinal"

  def __init__(
        self,
        category=None,
        value=None,
        comp=None,
        label=None,
        linking_feature=None):
    """

    Args:
      category (str): The type of the `LinkedData`,
       including `Entity`, `Type`, `Time` and `Ordinal`
      mention (Mention)
      comp (str): compare
      value (str): The actual value in Knowledge Base, such as mid, predicate, type etc.
      label (str): Label name, such as entity name, type name
      linking_feature: features
    """
    self.category = category
    self.value = value
    self.label = label
    self.comp = comp
    self.linking_feature = linking_feature
    self.mention = None

  def __str__(self):
    ret = "{} {} {} {} {} {}".format(
      self.category,
      self.mention.mention_text,
      self.comp,
      self.value,
      self.label,
      str(self.linking_feature))
    return ret
