from datetime import datetime


class Log(object):

  def __init__(self, level):
    self.ERROR = level == "error"
    self.DEBUG = self.ERROR or level == "debug"
    self.INFO = self.ERROR or self.DEBUG or level == "info"

  def error(self, mensagem):
    if self.ERROR:
      print("ERRO:::" + str(datetime.now()) + " -- " + str(mensagem))

  def debug(self, mensagem):
    if self.DEBUG:
      print("DEBUG::" + str(datetime.now()) + " -- " + str(mensagem))

  def info(self, mensagem):
    if self.INFO:
      print("INFO:::" + str(datetime.now()) + " -- " + str(mensagem))
