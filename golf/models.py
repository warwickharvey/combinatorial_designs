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

    def upper_bound(self):
        """
        Returns the best upper bound for this instance
        """
        if not self._upper_bound:
            bounds = GolfUpperBound.objects.filter(instance_id=self.id).order_by('num_rounds')
            if bounds:
                self._upper_bound = bounds[0]
            else:
                self._upper_bound = DummyBound()
        return self._upper_bound

    def lower_bound(self):
        """
        Returns the best lower bound for this instance, giving preference to
        those with solutions
        """
        if not self._lower_bound:
            # We don't seem to be able to easily order by whether or not there
            # is a solution corresponding to the bound, so just give preference
            # to solutions manually.
            bounds = GolfLowerBound.objects.filter(instance_id=self.id).order_by('-num_rounds')
            if not bounds:
                self._lower_bound = DummyBound()
            else:
                for bound in bounds:
                    if not self._lower_bound:
                        self._lower_bound = bound
                    if bound.num_rounds != self._lower_bound.num_rounds:
                        break
                    solution = bound.as_solution()
                    if solution:
                        self._lower_bound = solution
                        break
        return self._lower_bound

    def solution(self):
        """
        Returns the solution (if known) for the best lower bound for this
        instance
        """
        return self.lower_bound().as_solution()

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

    def as_solution(self):
        return None


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

    def as_solution(self):
        """
        Returns the GolfSolution corresponding to this bound, if there is one
        """
        try:
            solution = self.golfsolution
        except:
            solution = None
        return solution


class GolfSolution(GolfLowerBound):
    solution = models.TextField()
    normalised_solution = models.TextField(null=True)

    def as_solution(self):
        return self

