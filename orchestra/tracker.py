import itertools
import inspect
import ast

import orchestra.ast_util as ast_util

id_gen = itertools.count()
code = {}
nodes = {}
files = {}

class Tracker(object):
    def __init__(self, path):
        self.path = path
        files[path] = self

    def build_tracker(self, old_node, new_node):
        id_ = next(id_gen)
        expr = ast.Expression(new_node)
        ast.fix_missing_locations(expr)
        old_node.results = []
        nodes[id_] = old_node
        code[id_] = compile(expr, self.path, 'eval')
        return ast_util.function_call('%tracker.track_it', ast.Num(id_))

def track_it(id_):
    frame = inspect.stack()[1][0]
    result = eval(code[id_], frame.f_globals, frame.f_locals)
    node = nodes[id_]
    node.results.append(result)
    return result
