import argparse
from jnius import autoclass
from omniscient.kg import constant

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

  def sequential_query(self, qstrings):
    jqstrings = self.JArray.newInstance(self.JString, len(qstrings))
    for i in range(len(qstrings)):
      jqstrings[i] = self.JString(qstrings[i])
    results = self.tdbquery.sequentialQuery(jqstrings)
    sequential_result_list = []
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
      sequential_result_list.append(result_list)
    return sequential_result_list

  def parallel_query(self, qstrings, num_threads):
    parallel_result_list = []
    start_position = 0
    while start_position < len(qstrings):
      sub_qstrings = qstrings[start_position: start_position + constant.CHUNKING_SIZE]
      jsub_qstrings = self.JArray.newInstance(self.JString, len(sub_qstrings))
      for i in range(len(sub_qstrings)):
        jsub_qstrings[i] = self.JString(sub_qstrings[i])
      results = self.tdbquery.parallelQuery(jsub_qstrings, num_threads)
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
      start_position += constant.CHUNKING_SIZE
    return parallel_result_list

  def __del__(self):
    self.tdbquery.close()


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--index")
  argparser.add_argument("--query")
  args = argparser.parse_args()
  tdbquery = TDBQuery(args.index)
  print(args.query)
  results = tdbquery.query(args.query)
  print(results)