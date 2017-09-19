"""An implementation of the topological sorting algorithm."""


def sort(data, get_depencencies):
    """
    Topologically sort data.

    Arguments:
    - data - a dict from object ids to their dependencies.
    - get_depencencies - a function that gets a list of dependend object ids.
    Returns a list of object ids sorted topologically.
    """
    nodes = {}
    for key in data.keys():
        value = data[key]
        nodes[key] = _Node(value, get_depencencies(value))

    results = []
    while _visit_node(nodes, results):
        pass
    return results


def _visit_node(data, results):
    for key in data.keys():
        if not data[key].visited:
            _visit(data, key, results)
            return True
    return False


def _visit(data, key, results):
    value = data[key]
    if value.in_stack:
        raise ValueError("Not a DAG!")
    if value.visited:
        return

    value.in_stack = True
    for depencency in value.depencencies:
        _visit(data, depencency, results)
    value.visited = True
    value.in_stack = False
    results.append(key)


class _Node(object):  # pylint: disable=too-few-public-methods
    def __init__(self, value, depencencies):
        self.value = value
        self.depencencies = depencencies
        self.in_stack = False
        self.visited = False
