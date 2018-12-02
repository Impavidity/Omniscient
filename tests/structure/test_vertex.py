import pytest

from omniscient.structure import constant
from omniscient.structure.vertex import Vertex


class TestVertex(object):
  def test_grounding(self):
    v1 = Vertex(id=0, value="?x")
    v1.grounding(value="http://rdf.freebase.com/ns/m.010vz")
    assert v1.norm_grounded_value == ["ns:m.010vz"]
    v1.grounding(value="http://rdf.freebase.com/ns/m.060c4")
    assert v1.norm_grounded_value == ["ns:m.010vz", "ns:m.060c4"]
    assert v1.type == constant.VARIABLE
    v2 = Vertex(id=1, value='"1980-01-01"^^xsd:dateTime')
    assert v2.type == constant.LITERAL
    v3 = Vertex(id=2, value="http://rdf.freebase.com/ns/m.010vz")
    assert v3.type == constant.URI
    assert v3.norm_value == "ns:m.010vz"

