from django.db.models import Func
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Func, FloatField, Value

class WeightedTrigramSimilarity(Func):
    function = None  # Not needed because we’re wrapping another function
    template = "%(expressions)s"

    def __init__(self, expression, string, weight, **extra):
        weighted_similarity = TrigramSimilarity(expression, Value(string)) * weight
        super().__init__(weighted_similarity, output_field=FloatField(), **extra)