import gettext
_ = gettext.gettext

import models

MAX_NUM_GROUPS = 20
MAX_GROUP_SIZE = 20

class Constructor(object):
    """
    Base class for constructors
    """
    def __init__(self):
        user, _ = models.User.objects.get_or_create(
            name=self.name,
            email=self.email,
        )
        citation, _ = models.Citation.objects.get_or_create(citation=self.description)
        construction_info, _ = models.ConstructionInfo.objects.get_or_create(id=self.id, version=self.version)
        self.submission_info, _ = models.SubmissionInfo.objects.get_or_create(citation=citation, submitter=user, construction=construction_info)

    # TODO: Add a method for deleting (old) solutions/bounds created by this
    # constructor

    def construct(self, instance):
        bound = self.do_construct(instance)
        if bound:
            bound.save()
        return bound


class TrivialSolutionConstructor(Constructor):
    """
    Trivial solution constructor - constructs a two-round solution for any
    valid instance
    """
    id = 'golf_trivial_solution_constructor'
    version = 1
    name = 'Trivial solution constructor'
    email = 'warwick.harvey@gmail.com'
    description = 'Trivial two-round construction'

    def do_construct(self, instance):
        # TODO: Actually construct a solution rather than providing just the
        # bound
        return models.GolfLowerBound(instance=instance, submission_info=self.submission_info, num_rounds=2)


class TrivialUpperBoundConstructor(Constructor):
    """
    Trivial upper bound constructor - constructs an upper bound for any valid
    instance
    """
    id = 'golf_trivial_upper_bound_constructor'
    version = 1
    name = 'Trivial upper bound constructor'
    email = 'warwick.harvey@gmail.com'
    description = 'Trivial upper bound'

    def do_construct(self, instance):
        bound = (instance.num_players() - 1) / (instance.group_size - 1)
        return models.GolfUpperBound(instance=instance, submission_info=self.submission_info, num_rounds=bound)


class Constructors(object):
    """
    Class for managing and running Constructor instances
    """
    constructors = None
    _instances = None

    def __init__(self):
        self.constructors = [
            TrivialSolutionConstructor(),
            TrivialUpperBoundConstructor(),
        ]

    def instances(self):
        """
        Returns a list of all instances the constructors should be run on
        """
        if not self._instances:
            self._instances = []
            for num_groups in range(2, MAX_NUM_GROUPS + 1):
                for group_size in range(2, min(num_groups, MAX_GROUP_SIZE) + 1):
                    instance, _ = models.GolfInstance.objects.get_or_create(
                        num_groups=num_groups,
                        group_size=group_size,
                    )
                    self._instances.append(instance)
        return self._instances

    def construct_all(self):
        """
        Run all constructors on all instances
        """
        for constructor in self.constructors:
            for instance in self.instances():
                constructor.construct(instance)

