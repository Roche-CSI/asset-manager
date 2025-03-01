from math import ceil


class Paginator:
    @staticmethod
    def paginate(query, page_number, page_size=None):
        count = query.count()
        page_count = ceil(count / page_size) if page_size else 1
        if page_number and page_size:
            query = query.paginate(page_number, page_size)
        return query, page_count
