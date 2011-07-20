import ast

import mock

import orchestra.ast_util

def test_load_simple():
    node = orchestra.ast_util.load('var')
    print ast.dump(node)

    assert isinstance(node, ast.Name)
    assert node.id == 'var'
    assert isinstance(node.ctx, ast.Load)

def test_load_attr1():
    node = orchestra.ast_util.load('var1.var2')
    print ast.dump(node)

    assert isinstance(node, ast.Attribute)
    assert node.attr == 'var2'
    assert isinstance(node.ctx, ast.Load)
    node2 = node.value

    assert isinstance(node2, ast.Name)
    assert node2.id == 'var1'
    assert isinstance(node2.ctx, ast.Load)

def test_load_attr2():
    node = orchestra.ast_util.load('var1.var2.var3')
    print ast.dump(node)

    assert isinstance(node, ast.Attribute)
    assert node.attr == 'var3'
    assert isinstance(node.ctx, ast.Load)
    node2 = node.value

    assert isinstance(node2, ast.Attribute)
    assert node2.attr == 'var2'
    assert isinstance(node2.ctx, ast.Load)
    node3 = node2.value

    assert isinstance(node3, ast.Name)
    assert node3.id == 'var1'
    assert isinstance(node3.ctx, ast.Load)

def test_import():
    node = orchestra.ast_util.import_('test')
    print ast.dump(node)

    assert isinstance(node, ast.Import)
    assert len(node.names) == 1
    assert isinstance(node.names[0], ast.alias)
    assert node.names[0].name == 'test'
    assert node.names[0].asname == 'test'

def test_import_as():
    node = orchestra.ast_util.import_('test', 'test2')
    print ast.dump(node)

    assert isinstance(node, ast.Import)
    assert len(node.names) == 1
    assert isinstance(node.names[0], ast.alias)
    assert node.names[0].name == 'test'
    assert node.names[0].asname == 'test2'

@mock.patch('orchestra.ast_util.load')
def test_function_call(load):
    load.return_value = mock.sentinel.load 

    node = orchestra.ast_util.function_call(
        mock.sentinel.name,
        ast.Num(1),
        ast.Num(2),
        a=ast.Num(3),
        b=ast.Num(4),
    )
    print ast.dump(node)

    load.assert_called_with(mock.sentinel.name)

    assert isinstance(node, ast.Call)
    assert node.func == mock.sentinel.load
    assert node.args[0].n == 1
    assert node.args[1].n == 2

    assert isinstance(node.keywords[0], ast.keyword)
    assert node.keywords[0].arg == 'a'
    assert node.keywords[0].value.n == 3

    assert isinstance(node.keywords[1], ast.keyword)
    assert node.keywords[1].arg == 'b'
    assert node.keywords[1].value.n == 4

