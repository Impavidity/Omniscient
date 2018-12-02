from omniscient.structure import constant

class Edge(object):
  """
  Edge is the arc in QueryGraph or SubGraph
    representing URI, which is called predicate

  >>> e = Edge(id=0, value="http://rdf.freebase.com/ns/location.country.administrative_divisions")
  >>> e
  Edge(0: http://rdf.freebase.com/ns/location.country.administrative_divisions / ns:location.country.administrative_divisions)
  """

  def __init__(self, id, value, utils=None):
    """

    Args:
      id (int): Global Unique ID
      value (str): Edge value (URI)
    """
    self.id = id
    self.value = value
    self.utils = utils
    self.norm_value = self.normalization(value)

  def normalization(self, value):
    """
    Use prefix to shorten the uri.

    Args:
      value: complete uri or variable

    Returns:

    TODO:
      Currently this function only support freebase.
      Wrap this into a util which accept user-defined rules
    """
    if self.utils:
      pass
      """Apply the user-defined rule first, and then apply default rules"""
    value = value.replace(constant.FB_FULL, constant.FB_SHORT)
    return value

  def __hash__(self):
    return hash(self.id)

  def __eq__(self, other):
    return self.id == other.id

  def __str__(self):
    return f"{self.__class__.__name__}({self.id}: {self.value} / {self.norm_value})"

  __repr__ = __str__


if __name__ == "__main__":
  import doctest
  doctest.testmod()