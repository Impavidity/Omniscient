import argparse
import os
from jnius import autoclass

class TDBQuery(object):
  def __init__(self, path):
    self.path = path
    self.JString = autoclass('java.lang.String')
    self.JArray = autoclass("java.lang.reflect.Array")
    JTDBQuery = autoclass('botafogo/TDBQuery')
    self.tdbquery = JTDBQuery(self.JString(path))

  def query(self, qstring):
    results = self.tdbquery.query(self.JString(qstring))
    result_list = []
    for i in range(results.size()):
      query_solution = results.get(i)
      solution_dict = {}
      var_names = query_solution.varNames()
      while var_names.hasNext():
        var = var_names.next()
        string = query_solution.get(var).toString()
        solution_dict[var] = string
      result_list.append(solution_dict)
    return result_list

  def parallel_query(self, qstrings, num_threads):
    jqstrings = self.JArray.newInstance(self.JString, len(qstrings))
    for i in range(len(qstrings)):
      jqstrings[i] = self.JString(qstrings[i])
    results = self.tdbquery.parallelQuery(jqstrings, num_threads)
    parallel_result_list = []
    for i in range(results.size()):
      result = results.get(i)
      result_list = []
      for j in range(result.size()):
        query_solution = result.get(j)
        solution_dict = {}
        iter = query_solution.varNames()
        while iter.hasNext():
          var = iter.next()
          string = query_solution.get(var).toString()
          solution_dict[var] = string
        result_list.append(solution_dict)
      parallel_result_list.append(result_list)
    return parallel_result_list

  def __del__(self):
    os.remove(os.path.join(self.path, "journal.jrnl"))
    os.remove(os.path.join(self.path, "tdb.lock"))


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--index")
  argparser.add_argument("--query")
  args = argparser.parse_args()
  tdbquery = TDBQuery(args.index)
  print(args.query)
  results = tdbquery.query(args.query)
  print(results)