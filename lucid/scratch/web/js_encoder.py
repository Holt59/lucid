import base64
import numpy as np

def to_js(obj):
  """Convert python object to javascript expression."""
  
  if hasattr(obj, "__js__"):
    return obj.__js__()
  elif isinstance(obj, np.ndarray):
    return js_ndarray(obj, obj.dtype).__js__()
  elif isinstance(obj, str):
    return repr(obj)
  elif isinstance(obj, (int, float)):
    return str(obj)
  elif isinstance(obj, dict):
    pairs = [str(k) +": " + to_js(v) for k,v in obj.iteritems()]
    return "{" + ", ".join(pairs) + "}"
  elif isinstance(obj, list):
    return "[" + ", ".join([to_js(e) for e in obj]) + "]"
  else:
    raise RuntimeError("to_js(): unsupported type %s" % type(obj))
    
    
class JsExpr:
  """Represents a javascript expression in python."""

  def __init__(self, code):
    self.code = code

  def __repr__(self):
    return "JsExpr(\"\"\"%s\"\"\")" % self.code
  
  def __js__(self):
    return self.code


def js_ndarray(arr, dtype):
  arr    = np.asarray(arr, dtype)
  b64arr = base64.b64encode(arr)
  shape  = list(arr.shape)
  dtype  = str(dtype)

  code  = "(function () {\n"
  code += "  var s = \"%s\";\n" % b64arr
  code += "  var buffer = Uint8Array.from(atob(s), c => c.charCodeAt(0)).buffer;\n"
  code += "  var typed_arr = new %s(buffer);\n" % (dtype.capitalize() + "Array")
  code += "  return nj.array(typed_arr, '%s').reshape(%s);\n" % (dtype, shape)
  code += "})()\n"
  return JsExpr(code)
  