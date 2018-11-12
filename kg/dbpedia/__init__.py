import string

def unquotekey(key, encoding=None):
  """
  unquote a namespace key and turn it into a unicode string
  """

  valid_always = string.ascii_letters + string.digits

  output = []
  i = 0
  while i < len(key):
    if key[i] in valid_always:
      output.append(key[i])
      i += 1
    elif key[i] in '_-' and i != 0 and i != len(key):
      output.append(key[i])
      i += 1
    elif key[i] == '$' and i + 4 < len(key):
      # may raise ValueError if there are invalid characters
      output.append(chr(int(key[i + 1:i + 5], 16)))
      i += 5
    else:
      raise ValueError("unquote key saw invalid character '%s' at position %d" % (key[i], i))

  ustr = u''.join(output)

  if encoding is None:
    return ustr

  return ustr.encode(encoding)

if __name__ == "__main__":
  print(unquotekey('Barack_Hussein_Obama$002C_Jr$002E'))
