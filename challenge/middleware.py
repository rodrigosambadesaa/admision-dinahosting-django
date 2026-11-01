"""Security policy sent as an actual HTTP response header, not only a meta element."""


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        browser_fibonacci = request.path in {"/javascript/", "/JAVASCRIPT/index.html"}
        script_policy = "script-src 'self'; " if browser_fibonacci else "script-src 'none'; "
        response["Content-Security-Policy"] = (
            "default-src 'self'; " + script_policy + "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; "
            "form-action 'self'; frame-ancestors 'none'"
        )
        response["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "microphone=(), payment=(), usb=()"
        )
        response["Cross-Origin-Resource-Policy"] = "same-origin"
        response["X-Permitted-Cross-Domain-Policies"] = "none"
        return response
