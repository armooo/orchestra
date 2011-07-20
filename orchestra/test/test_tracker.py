import ast
import dis

import mock

import orchestra.tracker

def test_track_it():
    node = mock.Mock(name='node')
    node.results = []
    code = compile(ast.parse('obj()', mode='eval'), '<test>', 'eval')
    
    p1 = mock.patch.dict(orchestra.tracker.nodes, {'test': node})
    p2 = mock.patch.dict(orchestra.tracker.code, {'test': code})

    with p1, p2:
        obj = mock.Mock(name='obj')
        obj.return_value = mock.sentinel.obj_return

        result = orchestra.tracker.track_it('test')

    obj.assert_called_with()
    assert result == mock.sentinel.obj_return
    assert node.results[0] == mock.sentinel.obj_return

def test_tracker_register():
    with mock.patch.dict(orchestra.tracker.files, {}):
       tracker = orchestra.tracker.Tracker(mock.sentinel.path)
       assert orchestra.tracker.files[mock.sentinel.path] is tracker

def test_build_tracker():
    p1 = mock.patch.dict(orchestra.tracker.nodes, {})
    p2 = mock.patch.dict(orchestra.tracker.code, {})
    p3 = mock.patch.dict(orchestra.tracker.files, {})
    p4 = mock.patch('orchestra.tracker.id_gen')

    with p1, p2, p3, p4:
        def gen_id():
            while True:
                yield 1
        orchestra.tracker.id_gen = gen_id()

        old_node = mock.Mock(name='old_node')
        new_node = ast.parse('obj()', mode='eval').body
        print ast.dump(new_node)

        tracker = orchestra.tracker.Tracker('<test>')
        node = tracker.build_tracker(old_node, new_node)
        print ast.dump(node)

        assert hasattr(old_node, 'results')
        assert isinstance(old_node.results, list)

        assert isinstance(node, ast.Call)
        assert node.func.attr == 'track_it'
        assert node.func.value.id == '%tracker'
        assert len(node.args) == 1
        assert node.args[0].n == 1
        assert node.keywords == []


