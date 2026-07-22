from .context import reset_audit_context, set_audit_context


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        actor = request.user if request.user.is_authenticated else None
        tokens = set_audit_context(actor, request.headers.get("X-Farm-ID"))
        try:
            return self.get_response(request)
        finally:
            reset_audit_context(tokens)
