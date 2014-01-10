import gettext
_ = gettext.gettext

import models

MAX_NUM_GROUPS = 20
MAX_GROUP_SIZE = 20

class Constructor(object):
    """
    Base class for constructors
    """
    _submission_info = None

    @property
    def submission_info(self):
        """
        Returns a SubmissionInfo instance for use by the constructor.
        Assumes the subclass has defined the following fields for the
        constructor:
            id: A unique string ID
            version: An integer version number
            name: A human-readable name
            email: An email address for the author/maintainer
            description: A description
        """
        if not self._submission_info:
            user, _ = models.User.objects.get_or_create(
                name=self.name,
                email=self.email,
            )
            citation, _ = models.Citation.objects.get_or_create(citation=self.description)
            construction_info, _ = models.ConstructionInfo.objects.get_or_create(id=self.id, version=self.version)
            self._submission_info, _ = models.SubmissionInfo.objects.get_or_create(citation=citation, submitter=user, construction=construction_info)
        return self._submission_info

    def clear_constructions(self):
        """
        Deletes all constructions by this constructor from the database
        """
        self._submission_info = None
        models.ConstructionInfo.objects.filter(id=self.id).delete()

    def construct(self, instance):
        """
        Performs the construction for the given instance.  Returns the
        constructed item, or None if the construction is not applicable for
        this instance.
        Calls do_construct() to do the work, and then calls save() on the
        result, if any.
        """
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
        bound = (instance.num_players - 1) / (instance.group_size - 1)
        return models.GolfUpperBound(instance=instance, submission_info=self.submission_info, num_rounds=bound)


class Constructors(object):
    """
    Class for managing and running Constructor instances
    """
    _constructors = None
    _instances = None

    @property
    def constructors(self):
        if not self._constructors:
            self._constructors = [
                TrivialSolutionConstructor(),
                TrivialUpperBoundConstructor(),
            ]
        return self._constructors

    @property
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
            constructor.clear_constructions()
            for instance in self.instances:
                constructor.construct(instance)

