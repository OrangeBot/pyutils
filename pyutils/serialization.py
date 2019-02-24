import json
import os
from pyutils.fileworks import fix_path
import pickle


def load_json(where_from):
    if os.path.exists(fix_path(where_from)):
        with open(fix_path(where_from), 'r') as f:
            return json.load(f)
    else:
        return json.loads(where_from)


def dump_json(what, where, mode='w'):
    import json
    with open(fix_path(where), mode=mode) as f:
        return json.dump(what, f)


def load_pickle(where_from):
    if os.path.exists(fix_path(where_from)):
        with open(fix_path(where_from), 'rb') as f:
            return pickle.load(f)
    else:
        return pickle.loads(where_from)


def dump_pickle(what, where, mode='wb'):
    with open(fix_path(where), mode=mode) as f:
        return pickle.dump(what, f)


def load(where_from, engine=None):
    if engine in ['pkl', 'pickle'] or (engine is None and where_from.endswith('pkl')):
        return load_pickle(where_from)
    elif engine == 'json' or (engine is None and where_from.endswith('json')):
        return load_json(where_from)
    else:
        raise NotImplementedError("Unknown engine {}".format(engine))


def dump(what, where, engine='json'):
    if engine in ['pkl', 'pickle'] or (engine is None and where.endswith('pkl')):
        return dump_pickle(what, where, 'wb')
    elif engine == 'json' or (engine is None and where.endswith('json')):
        return dump_json(what, where, 'w')
    else:
        raise NotImplementedError("Unknown engine {}".format(engine))

