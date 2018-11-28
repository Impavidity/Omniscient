from omniscient.structure import constant

class Vertex(object):

  def __init__(self, id, value):
    self.id = id
    self.value = value
    self.type = self.get_type(value)

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

  def __str__(self):
    return f"{self.__class__.__name__}({self.id}: {self.value})"

  __repr__ = __str__