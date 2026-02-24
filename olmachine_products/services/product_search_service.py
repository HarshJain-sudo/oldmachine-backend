"""
Product search service: DB-only for now, extensible for Elasticsearch later.

TODO (later): Migrate product search to Elasticsearch; keep API and response
shape unchanged. Swap this implementation for one that queries ES and
returns filtered queryset or (ids, total_count).
"""

from django.db.models import Q, QuerySet


def get_product_queryset_for_search(
    queryset: QuerySet,
    search_term: str
) -> QuerySet:
    """
    Apply text search filter to product queryset.

    Currently uses DB only (Django ORM). Design is extensible: a future
    implementation can call Elasticsearch and return a queryset filtered
    by product IDs (or same interface with different backend).

    Args:
        queryset: Base Product queryset (already filtered by category etc.)
        search_term: Text to search in name and description

    Returns:
        Filtered queryset (products matching search_term)
    """
    if not search_term or not search_term.strip():
        return queryset
    term = search_term.strip()
    return queryset.filter(
        Q(name__icontains=term) | Q(description__icontains=term)
    )
