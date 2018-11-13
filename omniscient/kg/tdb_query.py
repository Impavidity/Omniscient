import argparse
from jnius import autoclass

class TDBQuery(object):
  def __init__(self, path):
    self.JString = autoclass('java.lang.String')
    self.JArray = autoclass("java.lang.reflect.Array")
    JTDBQuery = autoclass('botafogo/TDBQuery')
    self.tdbquery = JTDBQuery(self.JString(path))

  def query(self, qstring):
    results = self.tdbquery.query(self.JString(qstring))
    return results

  def parallel_query(self, qstrings, num_threads):
    jqstrings = self.JArray.newInstance(self.JString, len(qstrings))
    for i in range(len(qstrings)):
      jqstrings[i] = self.JString(qstrings[i])
    results = self.tdbquery.parallelQuery(jqstrings, num_threads)
    return results

if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--index")
  argparser.add_argument("--query")
  args = argparser.parse_args()
  qstring = """SELECT ?s ?p ?o
               WHERE { 
                    ?s ?p ?o .
                } LIMIT 10"""
  tdbquery = TDBQuery(path=args.index)
  print(qstring)
  results = tdbquery.query(qstring)
  for i in range(results.size()):
    query_solution = results.get(i)
    while query_solution.varNames().hasNext():
      var = query_solution.varNames().next()
      string = query_solution.get(var).toString()
      print(var, string)
  print(args.query)
  results = tdbquery.query(args.query)
  for i in range(results.size()):
    query_solution = results.get(i)
    while query_solution.varNames().hasNext():
      var = query_solution.varNames().next()
      string = query_solution.get(var).toString()
      print(var, string)
  # for i in range(results.size()):
  #   query_solution = results.get(i)
  #   iter = query_solution.varNames()
  #   while iter.hasNext():
  #     var = iter.next()
  #     print(var, query_solution.get(var).toString())
  #   print()
  # qstrings = [qstring] * 10
  # results = tdbquery.parallel_query(qstrings, 5)
  # for i in range(results.size()):
  #   result = results.get(i)
  #   for j in range(result.size()):
  #     query_solution = result.get(j)
  #     iter = query_solution.varNames()
  #     while iter.hasNext():
  #       var = iter.next()
  #       print(var, query_solution.get(var).toString())
  #     print()
  #   print()

