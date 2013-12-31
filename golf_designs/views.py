from django.shortcuts import render, get_object_or_404

from golf_designs.models import GolfInstance

def index(request):
    """
    Display list of all golf instances
    """
    instance_list = GolfInstance.objects.order_by('num_groups', 'group_size')
    context = {'instance_list': instance_list}
    return render(request, 'golf_designs/index.html', context)

def detail(request, num_groups, group_size):
    """
    Display details of the given golf instance
    """
    instance = get_object_or_404(GolfInstance, num_groups=num_groups, group_size=group_size)
    context = {
        'instance': instance,
    }
    return render(request, 'golf_designs/detail.html', context)

