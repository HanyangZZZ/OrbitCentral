from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Default pagination for all list endpoints.

    Query params:
      ?page=2           — page number
      ?page_size=10     — override default page size (max 100)
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
