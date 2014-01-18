from django.db.models import Min, Max
from django.shortcuts import render, get_object_or_404

from golf.models import GolfInstance

def index(request):
    """
    Display list of all golf instances
    """
    instance_list = GolfInstance.objects.order_by('group_size', 'num_groups')
    bounds = instance_list.aggregate(Min('group_size'), Max('group_size'), Min('num_groups'), Max('num_groups'))
    context = dict(bounds, instance_list=instance_list)
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

