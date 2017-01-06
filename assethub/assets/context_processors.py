
from assets.forms import SimpleSearchForm

def common_variables(request):
    form = SimpleSearchForm()
    return {'simple_search_form': form}

