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
        return '%s submitter=%s citation=%s' % (self.timestamp.date().isoformat(), unicode(self.submitter), unicode(self.citation))


class GolfInstance(models.Model):
    num_groups = models.IntegerField()
    group_size = models.IntegerField()

    class Meta:
        unique_together = ('num_groups', 'group_size')

    def __unicode__(self):
        return 'golf %dx%d' % (self.num_groups, self.group_size)

    def num_players(self):
        return self.num_groups * self.group_size

    def trivial_upper_bound(self):
        return (self.num_players - 1) / (self.group_size - 1)


class GolfUpperBound(models.Model):
    instance = models.ForeignKey(GolfInstance)
    submission_info = models.ForeignKey(SubmissionInfo)
    bound = models.IntegerField()

    def __unicode__(self):
        return '%s <= %d' % (unicode(self.instance), self.bound)


class GolfSolution(models.Model):
    instance = models.ForeignKey(GolfInstance)
    submission_info = models.ForeignKey(SubmissionInfo)
    num_rounds = models.IntegerField()
    solution = models.TextField()
    normalised_solution = models.TextField(null=True)

    def __unicode__(self):
        return '%s >= %d' % (unicode(self.instance), self.num_rounds)

