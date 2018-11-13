import os
import sys


if sys.platform == 'win32':
    separator = ';'
else:
    separator = ':'

tdbquery_jar = os.path.join(separator + os.path.dirname(os.path.realpath(__file__)), "../resource/tdbquery.jar")

if 'CLASSPATH' not in os.environ:
    os.environ['CLASSPATH'] = tdbquery_jar
else:
    os.environ['CLASSPATH'] += tdbquery_jar

from omniscient.kg import *