from itertools import izip

import mock

import orchestra.rewrite
import ast

def test_clone_visitor():
    code = """
class Test(object):
    def __init__(self, b=None):
        self.a = 2
        self.b = b
    """
    src_tree = ast.parse(code)

    visiter = orchestra.rewrite.CloneVisitor()
    new_tree = visiter.visit(src_tree)

    for old, new in izip(ast.walk(src_tree), ast.walk(new_tree)):
        assert old is not new
        assert old.__class__ == new.__class__
        assert old._attributes == new._attributes

        for attr in old._attributes:
            assert getattr(old, attr) == getattr(new, attr)


class TestExprTrackingNodeTransformer(object):
    def test_inject_import(self):
        tracker = mock.Mock(name='tracker')
        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)
        
        code = """
class Test(object):
    def __init__(self, b=None):
        self.a = 2
        self.b = b
        """
        module = ast.parse(code)
        new_module = etnf.visit(module)

        assert isinstance(new_module.body[0], ast.Import)
        assert len(new_module.body[0].names) == 1
        assert new_module.body[0].names[0].name == 'orchestra.tracker'
        assert new_module.body[0].names[0].asname == '%tracker'

    def test_instrment_default_args(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """
def test(a, b, c=dict()):
    pass
"""
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].args.defaults[0] is mock.sentinel.tracker

    def test_not_instrment_args(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """
def test(a, b, c=dict()):
    pass
"""
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].args.args[0] is not mock.sentinel.tracker
        assert new_module.body[1].args.args[1] is not mock.sentinel.tracker

    def test_not_instrment_store(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """a = 1"""
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].targets[0] is not mock.sentinel.tracker

    def test_instrment_load(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """a = 1"""
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].value is mock.sentinel.tracker

    def test_instrment_boolop(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """1 and 2"""
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].value is mock.sentinel.tracker

    def test_instrment_if(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """
if a or b:
    c = 0
else:
    c = 1
        """
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].test is mock.sentinel.tracker

    def test_instrment_while(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """
while a or b:
    pass
        """
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].test is mock.sentinel.tracker

    def test_instrment_for(self):
        tracker = mock.Mock(name='tracker')
        tracker.build_tracker.return_value = mock.sentinel.tracker

        etnf = orchestra.rewrite.ExprTrackingNodeTransformer(tracker)

        code = """
for a in b:
    pass
        """
        module = ast.parse(code)
        new_module = etnf.visit(module)

        print ast.dump(module)
        print ast.dump(new_module)
        assert new_module.body[1].iter is mock.sentinel.tracker

