import os
import sys

if sys.platform == 'win32':
    separator = ';'
else:
    separator = ':'

anserini_jar = os.path.join(separator + os.path.dirname(os.path.realpath(__file__)),
                            "../resource/jars/anserini-0.3.1-SNAPSHOT-fatjar.jar")
if 'CLASSPATH' not in os.environ:
  os.environ['CLASSPATH'] = anserini_jar
else:
  os.environ['CLASSPATH'] += anserini_jar

