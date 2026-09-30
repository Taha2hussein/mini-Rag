from .ContextQualityFilter import ContextQualityFilter
from .ContextQualityFilterInterface import (
    ContextQualityFilterInterface,
)


_filter_service: ContextQualityFilterInterface | None = None


def get_context_quality_filter() -> ContextQualityFilterInterface:

    global _filter_service

    if _filter_service is None:
        _filter_service = ContextQualityFilter()

    return _filter_service