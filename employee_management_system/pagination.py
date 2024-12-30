from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param, None)
            if page_size is not None:
                page_size = min(int(page_size), self.max_page_size)
                if page_size <= 0:
                    return self.page_size
                return page_size
        return self.page_size

    def get_paginated_response(self, data):
        return Response(
            {
                "status": "success",
                "code": 200,
                "message": "Employees fetched successfully.",
                "data": data,
            }
        )
