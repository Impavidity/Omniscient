from omniscient.structure import constant


class Triple(object):
  """
  Triple class comprises subject, predicate, and object strings,
    together with normalization function

  >>> from omniscient.structure.vertex import Vertex
  >>> from omniscient.structure.edge import Edge
  >>> triple = Triple(
  ...     sub=Vertex(id=0, value="?c"),
  ...     pred=Edge(id=0, value="http://rdf.freebase.com/ns/location.country.administrative_divisions"),
  ...     obj=Vertex(id=1, value="http://rdf.freebase.com/ns/m.010vz"))
  """

  def __init__(self, sub, pred, obj):
    """
    Args:
      sub (Vertex): subject
      pred (Edge): predicate
      obj (Vertex): object
    """
    self.subject = sub
    self.predicate = pred
    self.object = obj

  def __str__(self):
    return f"{self.__class__.__name__}({self.subject}, {self.predicate}, {self.object})"

  __repr__ = __str__


if __name__ == "__main__":
  import doctest
  doctest.testmod()