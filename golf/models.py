from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

import gettext
_ = gettext.gettext

class User(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=254)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.email)


class Citation(models.Model):
    citation = models.TextField()

    def __unicode__(self):
        return self.citation


class ConstructionInfo(models.Model):
    id = models.CharField(primary_key=True, max_length=80)
    version = models.IntegerField()

    def __unicode__(self):
        return '%s, version %d' % (self.id, self.version)


class SubmissionInfo(models.Model):
    citation = models.ForeignKey(Citation)
    submitter = models.ForeignKey(User)
    construction = models.ForeignKey(ConstructionInfo, null=True)
    timestamp = models.DateTimeField('date submitted', auto_now_add=True)

    def __unicode__(self):
        return '%s (%s %s)' % (unicode(self.citation), unicode(self.submitter), self.timestamp.date().isoformat())


class GolfInstance(models.Model):
    num_groups = models.IntegerField(validators=[MinValueValidator(2)])
    group_size = models.IntegerField(validators=[MinValueValidator(2)])
    _upper_bound = None
    _lower_bound = None

    class Meta:
        unique_together = ('num_groups', 'group_size')
        index_together = [
            ['num_groups', 'group_size'],
        ]

    def __init__(self, *args, **kwargs):
        super(GolfInstance, self).__init__(*args, **kwargs)
        # Can't do a full_clean() or validation complains about already having
        # an instance with this ID, etc. when loading an instance from the
        # database, but validate what we can...
        self.clean_fields()
        self.clean()

    def __unicode__(self):
        return '%dx%d' % (self.num_groups, self.group_size)

    def clean(self):
        super(GolfInstance, self).clean()
        # Don't allow instances with fewer groups than the group size
        if self.num_groups < self.group_size:
            raise ValidationError(
                _('Golf instances must have at least as many groups as the group size.'),
                code='fewer_groups_than_group_size',
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(GolfInstance, self).save(*args, **kwargs)

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

