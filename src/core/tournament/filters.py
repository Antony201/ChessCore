from datetime import datetime

from django_filters import rest_framework as filters


class TournamentFilters(filters.FilterSet):
    time = filters.ChoiceFilter(
        choices=(
            ("current", "текущие"),
            ("future", "будущие"),
            ("finished", "завершённые"),
        ),
        method="time_filter",
    )

    def time_filter(self, queryset, name, value):
        query_filters = {}

        if name == "time":
            if value == "current":
                query_filters["start_at__lte"] = datetime.now()
                query_filters["finished"] = False
            elif value == "future":
                query_filters["start_at__gte"] = datetime.now()
                query_filters["finished"] = False
            elif value == "finished":
                query_filters["finished"] = True

        return queryset.filter(**query_filters)
