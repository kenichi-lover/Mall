

from django.http import HttpResponse
import time
from django.views.decorators.cache import cache_page

@cache_page(10)
def index_view(request):
    return HttpResponse(time.time())