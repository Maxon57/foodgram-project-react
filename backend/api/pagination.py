from rest_framework.pagination import PageNumberPagination

from foodgram.settings import PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """
    Задает пагинацию на страницы и добавляет дополнительный
    параметр limit.
    """
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
