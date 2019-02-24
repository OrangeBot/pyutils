import threading
import os


def trim(l, s=None, e=None):
    if s is not None and l.startswith(s) and len(s) > 0:
        l = l[len(s):]
    if e is not None and l.endswith(e) and len(e) > 0:
        l = l[:-len(e)]
    return l

def get_source_code(func):
    import inspect
    lines = inspect.getsourcelines(func)[0]

    # define tabulation:
    import re

    tabulation = re.findall(r'(\s*)', lines[0])[0]
    return ''.join([trim(l, s=tabulation) for l in lines])


def create_script_from_method(func, path, add_shortcuts=True):
    import os
    import inspect
    name = func.__name__
    if os.path.isdir(path):
        # get method name
        path = os.path.join(path, name)
    if not '.' in path:
        path = path + '.py'

    script_code = """#!python
from __future__ import print_function"""

    # arguments
    argspec = inspect.getargspec(func)
    # argparse
    if len(argspec.args) > 0:
        script_code += """
import argparse
parser = argparse.ArgumentParser()

"""

        k = len(argspec.args) - len(argspec.defaults)

        for i, arg in enumerate(argspec.args):
            arg_line = "parser.add_argument('--{arg}'".format(arg=arg)
            if add_shortcuts:
                comps = arg.split('_')
                if len(comps) > 1:
                    arg_line += ", '--{short_arg}'".format(short_arg=''.join([c[0] for c in comps]))
                elif len(arg) > 1:
                    arg_line += ", '-{short_arg}'".format(short_arg=comps[0][0])
            if i >= k:
                # default
                arg_line += ", default={default}".format(default=repr(argspec.defaults[i - k]))
            else:
                arg_line += ", required=True"
            arg_line += ')\n'
            script_code += arg_line
        script_code += """
args = parser.parse_args()
"""

    # source_code
    script_code += get_source_code(func)

    script_code += """
if __name__ == "__main__":
    result = {func_name}({args})
    if result is not None:
        print(result)
""".format(func_name=name, args=', '.join(['args.' + arg for arg in argspec.args]))

    write(script_code, path)


def run_bg(target, *args, **kwargs):
    t = threading.Thread(target=target, args=args, kwargs=kwargs)
    t.start()
    return t



class Mock(object):
    def __init__(self, prototype=None, dump_path=None, dump_engine='json'):
        type_sc = {
            'pickle': 'pkl',
            'pkl': 'pkl',
            'json': 'json',
        }
        if type(prototype) is type:
            self._prototype = None
            self.ptt = prototype
        else:
            self._prototype = prototype
            self.ptt = type(prototype)
        self.dump_engine = dump_engine
        if dump_path is None:
            dump_path = os.path.join("data", "mock_" + type(self.prototype).__name__ + '.' + type_sc[dump_engine])
        self.dump_path = dump_path
        if os.path.exists(self.dump_path):
            self.mock = load(self.dump_path, engine=self.dump_engine)
        else:
            self.mock = dict()

    @property
    def prototype(self):
        if self._prototype is None:
            self._prototype = self.ptt()
        return self._prototype

    def __getattr__(self, item):
        # triggers only when object not in class attributes already
        if self.prototype is None:
            if item in self.mock:
                res = self.mock[item]
                try:
                    res.__call__ = lambda self_: self_
                except:
                    pass
                return res
            else:
                raise AttributeError("Item '{}' is not mocked and no prototype object is given.".format(item))
        import types
        # if isinstance(getattr(self.prototype, item), types.MethodType):
        # might fail on getattr call. Instead, do following:
        if hasattr(self.ptt, item) and isinstance(getattr(self.ptt, item), types.FunctionType):
            # it's a method
            if item in self.mock:
                return lambda *args, **kwargs: self.mock[item]
            else:
                def mock_extractor(*args, **kwargs):
                    print("WARNING: No mocked value for key '{}', trying to retrieve value from prototype".format(item))
                    self.mock[item] = getattr(self.prototype, item)(*args, **kwargs)
                    dump(self.mock, self.dump_path, self.dump_engine)
                    return self.mock[item]
                return mock_extractor
        else:
            # it's an attribute
            if item not in self.mock:
                print("WARNING: No mocked value for key '{}', trying to retrieve value from prototype".format(item))
                try:
                    self.mock[item] = getattr(self.prototype, item)
                    dump(self.mock, self.dump_path, self.dump_engine)
                except Exception as e:
                    raise AttributeError("Failed to extract value of '{}' from prototype, error: \n{}".format(item, e))
            return self.mock[item]
