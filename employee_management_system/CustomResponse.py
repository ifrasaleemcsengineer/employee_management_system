from rest_framework.response import Response


class CustomResponse(Response):

    def __init__(self, status_code, message, data=None):
        response_data = {
            "status": "success" if 200 <= status_code < 300 else "error",
            "code": status_code,
            "message": message,
            "data": data if data is not None else {},
        }
        super().__init__(data=response_data, status=status_code)
