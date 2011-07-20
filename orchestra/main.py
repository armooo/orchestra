import sys
import imp
import os.path
import ast
import pprint

import orchestra.rewrite
import orchestra.tracker

hook = orchestra.rewrite.CoverageHook()

def install_hook():
    if not hook in sys.meta_path:
        sys.meta_path.insert(0, hook)

def uninstall_hook():
    if hook in sys.meta_path:
        sys.meta_path.remove(hook)

def run_path(path, args):
    old_main = sys.modules['__main__']
    sys.modules['__main__'] = imp.new_module('__main__')

    old_path = sys.path[0]
    sys.path[0] = os.path.dirname(os.path.abspath(path))

    old_argv = sys.argv
    sys.argv = args

    try:
        code = orchestra.rewrite.rewrite_path(path)
        eval(code, sys.modules['__main__'].__dict__)
    finally:
        sys.modules['__main__'] = old_main
        sys.path[0] = old_path
        sys.argv = old_argv

def report():
    for path, tracker in orchestra.tracker.files.items():
        print '#'*70
        print path
        print '#'*70

        for node in ast.walk(tracker.tree):
            if hasattr(node, 'results'):
                print '*' * 20
                print ast.dump(node)
                pprint.pprint(node.results)
                print '*' * 20
                print

def cover(script_path, argv):
    install_hook()
    run_path(script_path, argv[1:])
    uninstall_hook()
    report()

if __name__ == '__main__':
    script_path = sys.argv[1]
    cover(script_path, sys.argv[1:])

