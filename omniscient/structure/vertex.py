from omniscient.structure import constant

class Vertex(object):
  """
  Vertex is the node in a QueryGraph or SubGraph,
    representing URI, literal value or variable

  >>> v = Vertex(id=0, value="?x")
  >>> v
  Vertex(0: ?x / ?x, variable)
  >>> v = Vertex(id=1, value='"1980-01-01"^^xsd:dateTime')
  >>> v
  Vertex(1: "1980-01-01"^^xsd:dateTime / "1980-01-01"^^xsd:dateTime, literal)
  >>> v = Vertex(id=2, value="http://rdf.freebase.com/ns/m.010vz")
  >>> v
  Vertex(2: http://rdf.freebase.com/ns/m.010vz / ns:m.010vz, uri)

  """

  def __init__(self, id, value, utils=None):
    """

    Args:
      id (int): Global Unique ID
      value (str): Vertex value (URI, literal value or variable (starts with `?`))
    """
    self.id = id
    self.value = value
    self.type = self.get_type(value)
    self.utils = utils
    self.norm_value = self.normalization(value)
    self.grounded_value = []
    self.norm_grounded_value = []
    if self.type == constant.URI:
      self.grounding(self.value)

  def grounding(self, value):
    self.grounded_value.append(value)
    self.norm_grounded_value.append(self.normalization(value))

  def __hash__(self):
    return hash(self.id)

  def __eq__(self, other):
    return self.id == other.id

  @staticmethod
  def get_type(value):
    if value.startswith('?'):
      return constant.VARIABLE
    elif value.startswith('"'):
      return constant.LITERAL
    else:
      return constant.URI

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
    value = value.replace(constant.XSD_FULL, constant.XSD_SHORT)
    return value

  def __str__(self):
    return f"{self.__class__.__name__}({self.id}: {self.value} / {self.norm_value}, {self.type})"

  __repr__ = __str__


if __name__ == "__main__":
  import doctest
  doctest.testmod()