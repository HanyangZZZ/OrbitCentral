from rest_framework.pagination import CursorPagination, PageNumberPagination


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


class ReviewCursorPagination(CursorPagination):
    """
    Cursor-based pagination for reviews — ideal for infinite scroll.

    Returns ``next`` / ``previous`` opaque cursor URLs.  No COUNT query,
    no items shifting when new reviews are inserted mid-scroll.

    Query params:
      ?cursor=<opaque>  — cursor from a previous ``next`` / ``previous`` link
      ?page_size=10     — override default page size (max 50)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    ordering = '-created_at'
