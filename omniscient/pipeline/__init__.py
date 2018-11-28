import sys
import os

if sys.platform == 'win32':
    separator = ';'
else:
    separator = ':'

stanfordnlp_jar = os.path.join(separator + os.path.dirname(os.path.realpath(__file__)), "../resource/stanford-corenlp-3.9.2.jar")
protobuf_jar = os.path.join(separator + os.path.dirname(os.path.realpath(__file__)), "../resource/protobuf-java-3.2.0.jar")

if 'CLASSPATH' not in os.environ:
    os.environ['CLASSPATH'] = stanfordnlp_jar + protobuf_jar
else:
    os.environ['CLASSPATH'] += stanfordnlp_jar + protobuf_jar
