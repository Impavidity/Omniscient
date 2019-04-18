import weakref

class Mention(object):
  def __init__(
        self,
        start=None,
        end=None,
        mention_text=None,
        linked_data_list=None):
    self.start = start
    self.end = end
    self.span = (start, end)
    self.mention_text = mention_text
    self.linked_data_list = linked_data_list or []
    # If linked_data_list is not None, then link mention to each linked data

  def add_linked_data(self, linked_data):
    """
    Currently the adding process will ignore the deduplicate process
    Args:
      linked_data:

    Returns:

    """
    linked_data.mention = self
    self.linked_data_list.append(linked_data)

  def __str__(self):
    header = "{}\t{}\n".format(self.mention_text, self.span)
    for linked_data in self.linked_data_list:
      header += "\t{}\n".format(linked_data)
    return header