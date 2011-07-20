import ast

def load(name):
    load  = None
    for part in name.split('.'):
        if not load:
            load = ast.Name(id=part, ctx=ast.Load())
        else:
            load = ast.Attribute(value=load, attr=part, ctx=ast.Load())
    return load

def function_call(name, *arg, **kargs):
    args = list(arg)
    keywords = [ast.keyword(arg=k, value=v) for k, v in kargs.items()]
    return ast.Call(func=load(name), args=args, keywords=keywords, starargs=None, kwargs=None)

def import_(name, as_name=None):
    if not as_name:
        as_name = name
    return ast.Import([ast.alias(name=name, asname=as_name)])

