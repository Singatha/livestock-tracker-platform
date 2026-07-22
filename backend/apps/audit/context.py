from contextvars import ContextVar

_audit_actor = ContextVar("audit_actor", default=None)
_audit_farm_id = ContextVar("audit_farm_id", default=None)


def set_audit_context(actor, farm_id):
    return _audit_actor.set(actor), _audit_farm_id.set(farm_id)


def reset_audit_context(tokens):
    _audit_actor.reset(tokens[0])
    _audit_farm_id.reset(tokens[1])


def audit_context():
    return _audit_actor.get(), _audit_farm_id.get()
