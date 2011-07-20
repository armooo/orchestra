import imp
import ast
import sys
import copy

import orchestra.ast_util as ast_util
from orchestra.tracker import Tracker

def rewrite_path(path):
    with open(path) as file_:
        src_tree = ast.parse(file_.read(), path)
        tracker = Tracker(path, src_tree)
        mod_tree = ExprTrackingNodeTransformer(tracker).visit(src_tree)
        ast.fix_missing_locations(mod_tree)

        return compile(mod_tree, path, 'exec')

class CoverageHook(object):
    def __init__(self):
        self.module_code = {}

    def find_module(self, name, path=None):
        file_, path, desc = imp.find_module(name, path)
        file_.close()
        if desc[2] != imp.PY_SOURCE:
            return None

        self.module_code[name] = rewrite_path(path)

        return self

    def load_module(self, name):
        mod = imp.new_module(name)
        co = self.module_code.pop(name)
        eval(co, mod.__dict__)
        sys.modules[name] = mod
        return mod


class CloneVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        return self.clone(node, True)

    def clone(self, node, recurse=False):
        if not isinstance(node, ast.AST):
            return node

        new_node = node.__class__()
        for attr in node._attributes:
            setattr(new_node, attr, getattr(node, attr))

        for field in node._fields:
            value = getattr(node, field)
            if value is None:
                setattr(new_node, field, None)
            elif isinstance(value, list):
                new_value = []
                setattr(new_node, field, new_value)
                for item in value:
                    if recurse:
                        item = self.visit(item)
                    new_value.append(item)
            else:
                if recurse:
                    value = self.visit(value)
                setattr(new_node, field, value)

        return new_node


class ExprTrackingNodeTransformer(CloneVisitor):
    def __init__(self, tracker):
        super(ExprTrackingNodeTransformer, self).__init__()
        self.tracker = tracker

    def visit_Module(self, node):
        """
        Inject our module
        """
        node = self.generic_visit(node)
        node.body.insert(0, ast_util.import_('orchestra.tracker', '%tracker'))
        return node

    def visit_arguments(self, node):
        """
        Only process the default arguments
        """
        new_node = self.clone(node)
        new_node.defaults = []
        for default in (node.defaults or []):
            new_node.defaults.append(self.visit(default))
        return new_node

    def generic_visit(self, node):
        new_node = super(ExprTrackingNodeTransformer, self).generic_visit(node)
        if not isinstance(new_node, ast.expr):
            return new_node
        if hasattr(new_node, 'ctx') and isinstance(new_node.ctx, ast.Store):
            return new_node

        return self.tracker.build_tracker(node, new_node)

