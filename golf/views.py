from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Min, Max
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from golf.models import GolfInstance

def index(request):
    """
    Display table of all golf instances
    """
    instances = GolfInstance.objects.order_by('num_groups', 'group_size')
    bounds = instances.aggregate(Min('group_size'), Max('group_size'), Min('num_groups'), Max('num_groups'))
    num_groups_range = range(bounds['num_groups__min'], bounds['num_groups__max'] + 1)
    group_size_range = range(bounds['group_size__min'], bounds['group_size__max'] + 1)
    idx = 0
    array = [[None] + group_size_range]
    for num_groups in num_groups_range:
        row = [num_groups]
        for group_size in group_size_range:
            if idx < len(instances) and group_size == instances[idx].group_size and num_groups == instances[idx].num_groups:
                row.append(instances[idx])
                idx += 1
            else:
                row.append(None)
        array.append(row)
    # There shouldn't be any instances left over, but we put them into the
    # context anyway so that in the tests we can check that there really aren't
    # any.
    context = {'instance_array': array, 'left_over_instances': instances[idx:]}
    return render(request, 'golf/index.html', context)

def detail(request, num_groups, group_size):
    """
    Display details of the given golf instance
    """
    instance = get_object_or_404(GolfInstance, num_groups=num_groups, group_size=group_size)
    context = {
        'instance': instance,
    }
    return render(request, 'golf/detail.html', context)

def submit_upper_bound(request, num_groups, group_size):
    """
    Allow submission of a new upper bound
    """
    instance = get_object_or_404(GolfInstance, num_groups=num_groups, group_size=group_size)
    if request.method == 'POST':
        upper_bound = request.POST['num_rounds']
        messages.info(request, 'You submitted an upper bound of %s.' % upper_bound)
        return HttpResponseRedirect(reverse('golf:detail', args=(num_groups, group_size)))
    else:
        instance = get_object_or_404(GolfInstance, num_groups=num_groups, group_size=group_size)
        context = {
            'instance': instance,
        }
        return render(request, 'golf/submit_upper_bound.html', context)


