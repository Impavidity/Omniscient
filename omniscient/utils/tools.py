from multiprocessing import Lock, Value

class Counter(object):
  def __init__(self):
    self.value = 0

  def increment_and_get(self):
    self.value += 1
    return self.value

  def get_and_increment(self):
    value = self.value
    self.value += 1
    return value


class AtomicCounter(object):
  def __init__(self):
    self.value = Value("i", 0)
    self.lock = Lock()

  def increment(self):
    with self.lock:
      self.value.value += 1
      return self.value.value


class PredicateFilter(object):
  def __init__(self):
    pass

  def is_valid(self, predicate):
    return True