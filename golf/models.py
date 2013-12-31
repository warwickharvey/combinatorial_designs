from django.db import models

class User(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=254)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.email)


class Citation(models.Model):
    citation = models.TextField()

    def __unicode__(self):
        return self.citation


class SubmissionInfo(models.Model):
    citation = models.ForeignKey(Citation)
    submitter = models.ForeignKey(User)
    timestamp = models.DateTimeField('date submitted', auto_now_add=True)

    def __unicode__(self):
        return '%s (%s %s)' % (unicode(self.citation), unicode(self.submitter), self.timestamp.date().isoformat())


class GolfInstance(models.Model):
    num_groups = models.IntegerField()
    group_size = models.IntegerField()
    _upper_bound = None
    _lower_bound = None

    class Meta:
        unique_together = ('num_groups', 'group_size')
        index_together = [
            ['num_groups', 'group_size'],
        ]

    def __unicode__(self):
        return '%dx%d' % (self.num_groups, self.group_size)

    def name(self):
        """
        Returns a short, unique, meaningful name identifying this instance
        """
        return unicode(self)

    def num_players(self):
        """
        Number of players for this instance
        """
        return self.num_groups * self.group_size

    def trivial_upper_bound(self):
        return (self.num_players - 1) / (self.group_size - 1)

    def bound_if_defined(self, bounds):
        """
        Returns the first GolfBound instance in bounds if it exists;
        otherwise returns a dummy instance
        """
        if bounds:
            return bounds[0]
        else:
            return DummyBound()

    def upper_bound(self):
        """
        Returns the best upper bound for this instance
        """
        if not self._upper_bound:
            bounds = GolfUpperBound.objects.filter(instance_id=self.id).order_by('num_rounds')
            self._upper_bound = self.bound_if_defined(bounds)
        return self._upper_bound

    def lower_bound(self):
        """
        Returns the best lower bound for this instance
        """
        if not self._lower_bound:
            bounds = GolfLowerBound.objects.filter(instance_id=self.id).order_by('-num_rounds', 'golfsolution')
            self._lower_bound = self.bound_if_defined(bounds)
        return self._lower_bound

    def solution(self):
        """
        Returns the solution (if known) for the best lower bound for this
        instance
        """
        try:
            solution = self.lower_bound().golfsolution
        except:
            solution = None
        return solution

    def is_closed(self):
        """
        Is a closed instance (upper and lower bounds are the same)
        """
        l = self.lower_bound()
        u = self.upper_bound()
        if isinstance(l, DummyBound) or isinstance(u, DummyBound):
            return False
        else:
            return u.num_rounds == l.num_rounds


class DummyBound(object):
    num_rounds = 'unknown'
    submission_info = {'citation': 'No info'}


class GolfBound(models.Model):
    instance = models.ForeignKey(GolfInstance)
    submission_info = models.ForeignKey(SubmissionInfo)
    num_rounds = models.IntegerField()


class GolfUpperBound(GolfBound):
    def __unicode__(self):
        return '%s <= %d' % (unicode(self.instance), self.num_rounds)


class GolfLowerBound(GolfBound):
    def __unicode__(self):
        return '%s >= %d' % (unicode(self.instance), self.num_rounds)


class GolfSolution(GolfLowerBound):
    solution = models.TextField()
    normalised_solution = models.TextField(null=True)


