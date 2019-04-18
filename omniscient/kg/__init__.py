import os
import sys


if sys.platform == 'win32':
  separator = ';'
else:
  separator = ':'

tdbquery_jar = os.path.join(separator + os.path.dirname(os.path.realpath(__file__)), "../resource/jars/tdbquery.jar")

if 'CLASSPATH' not in os.environ:
  os.environ['CLASSPATH'] = tdbquery_jar
else:
  os.environ['CLASSPATH'] += tdbquery_jar
#
# jnius_config.add_options('-Xmx40960m')
# import kg
# from omniscient.kg import *