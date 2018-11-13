import gzip
import logging

from omniscient.kg.freebase.freebase_node import FreebaseNode


logging.basicConfig()
LOGGER = logging.getLogger("Freebase")
LOGGER.setLevel(logging.INFO)
TRIPLE_SPLITTER = '\t'


class Freebase(object):
  def __init__(self, input_path):
    if input_path.endswith(".gz"):
      self.f = gzip.open(input_path, 'rb')
    else:
      self.f = open(input_path, 'rb')
    self.atEOF = False
    self.current_node = None
    self.node = None
    self.line_counter = 0

  # def clear_graph(self):
  #   self.g = Graph()

  def __iter__(self):
    return self

  def __next__(self):
    while True:
      if self.atEOF:
        raise StopIteration
      try:
        line = self.f.readline()
        self.line_counter += 1
        if not line:
          self.node = self.current_node
          self.atEOF = True
          break
        else:
          line = line.decode("utf-8")
          if not line.startswith("#") and not line.strip() == "":
            # Ignore comments and empty lines.
            triple = line.split(TRIPLE_SPLITTER)
            if len(triple) != 4:
              # subject predicate object .\n
              LOGGER.warning("Ignoring invalid NT triple line: {}", line)
              continue
            # self.g.parse(data="{} {} {} .".format(triple[0], triple[1], triple[2]), format="nt")
            # triple = iter(self.g.__iter__()).__next__()
            # self.clear_graph()
            if self.current_node is None:
              # First line with a valid triple, create a new node.
              self.current_node = FreebaseNode(triple[0])
              self.current_node.add_predicate_value(triple[1], triple[2])
              continue
            if triple[0] == self.current_node.uri:
              # Same URI, still processing the same node.
              self.current_node.add_predicate_value(triple[1], triple[2])
            else:
              self.node = self.current_node
              self.current_node = FreebaseNode(triple[0])
              self.current_node.add_predicate_value(triple[1], triple[2])
              break
      except IOError:
        LOGGER.error("Cannot read next line from reader!")
        exit()
    return self.node

  def close(self):
    if self.f:
      self.f.close()

if __name__ == "__main__":
  freebase = Freebase("/tuna1/collections/freebase/freebase-rdf-latest.gz")
  for freebase_node in freebase:
    print(freebase_node)
    break