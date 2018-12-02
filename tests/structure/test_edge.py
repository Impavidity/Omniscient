import pytest

from omniscient.structure.edge import Edge


class TestEdge(object):
  def test_normalization(self):
    e = Edge(id=0, value="http://rdf.freebase.com/ns/location.country.administrative_divisions")
    assert e.norm_value == "ns:location.country.administrative_divisions"