import json
import logging

logger = logging.getLogger("custom_logger")


class CustomLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_body = request.body
        request._body = request_body
        self.log_request(request)
        response = self.get_response(request)
        self.log_response(response)

        return response

    def log_request(self, request):
        method = request.method
        path = request.path
        ip = self.get_client_ip(request)

        if method in ["POST", "PUT"]:
            body = self.get_request_body(request)

            if body:
                body_data = (
                    json.dumps(body, indent=2) if isinstance(body, dict) else body
                )
                body_log = f", Body: {body_data}"
            else:
                body_log = ""

            logger.info(f"Incoming Request: {method} {path}, IP: {ip}{body_log}")
        else:
            logger.info(f"Incoming Request: {method} {path}, IP: {ip}")

    def log_response(self, response):
        status_code = response.status_code
        content_type = response.get("Content-Type", "")

        if status_code >= 400:
            logger.error(
                f"Response Status: {status_code}, Content-Type: {content_type}"
            )
        else:
            logger.info(f"Response Status: {status_code}, Content-Type: {content_type}")

    def get_request_body(self, request):
        """Return request body based on content type."""
        try:
            request_body = getattr(request, "_body", None)

            if request.content_type == "application/json" and request_body:
                return json.loads(request_body.decode("utf-8"))

            elif (
                request.content_type == "application/x-www-form-urlencoded"
                and request_body
            ):
                return request.POST.dict()

            return None
        except Exception as e:
            logger.error(f"Error parsing body: {e}")
            return None

    def get_client_ip(self, request):
        """Get the IP address of the client making the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
