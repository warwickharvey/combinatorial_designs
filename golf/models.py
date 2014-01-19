from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

import gettext
_ = gettext.gettext


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

    @property
    def name(self):
        """
        Returns a short, unique, meaningful name identifying this instance
        """
        return unicode(self)

    @property
    def num_players(self):
        """
        Number of players for this instance
        """
        return self.num_groups * self.group_size

    @property
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

    @property
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

    @property
    def solution(self):
        """
        Returns the solution (if known) for the best lower bound for this
        instance
        """
        return self.lower_bound.as_solution()

    @property
    def is_closed(self):
        """
        Is a closed instance (upper and lower bounds are the same)
        """
        l = self.lower_bound
        u = self.upper_bound
        if isinstance(l, DummyBound) or isinstance(u, DummyBound):
            return False
        else:
            return u.num_rounds == l.num_rounds

    @property
    def bound_range(self):
        """
        Returns a string representation of the range of the bounds on this
        instance
        """
        l = self.lower_bound
        u = self.upper_bound
        if l.num_rounds == u.num_rounds:
            return str(l.num_rounds)
        else:
            return u'%d - %d' % (l.num_rounds, u.num_rounds)


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
    solution_string = models.TextField()
    normalised_solution_string = models.TextField(blank=True)

    _solution = None

    def clean(self):
        super(GolfSolution, self).clean()
        self.validate_solution_string(self.solution_string)
        if self.normalised_solution_string:
            self.validate_solution_string(self.normalised_solution_string)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(GolfSolution, self).save(*args, **kwargs)

    def as_solution(self):
        return self

    @staticmethod
    def solution_string_to_array(string):
        return [[[int(player) for player in group.split(',')] for group in round.split('|')] for round in string.split('\n')]

    @staticmethod
    def solution_array_to_string(array):
        return '\n'.join(['|'.join([','.join([str(player) for player in group]) for group in round]) for round in array])

    def validate_solution_string(self, string):
        array = GolfSolution.solution_string_to_array(string)
        if len(array) != self.num_rounds:
            raise ValidationError(
                _('Golf solution has %(actual)d rounds; expected %(expected)d.'),
                code='wrong_number_of_rounds',
                params={
                    'actual': len(array),
                    'expected': self.num_rounds,
                },
            )
        player_set = set()
        pair_map = {}
        for round_index, round in enumerate(array):
            round_num = round_index + 1
            if len(round) != self.instance.num_groups:
                raise ValidationError(
                    _('Golf solution only has %(actual)d groups in round %(round)d; expected %(expected)d.'),
                    code='wrong_number_of_groups_in_round',
                    params={
                        'actual': len(round),
                        'expected': self.instance.num_groups,
                        'round': round_num,
                    },
                )
            player_map = {}
            for group_index, group in enumerate(round):
                group_num = group_index + 1
                if len(group) != self.instance.group_size:
                    raise ValidationError(
                        _('Golf solution has %(actual)d players in group %(group)d of round %(round)d; expected %(expected)d.'),
                        code='wrong_number_of_players_in_group',
                        params={
                            'actual': len(group),
                            'expected': self.instance.group_size,
                            'group': group_num,
                            'round': round_num,
                        },
                    )
                for player in group:
                    player_set.add(player)
                    if player in player_map:
                        raise ValidationError(
                            _('Player %(player)s appears in groups %(group1)d and %(group2)d in round %(round)d.'),
                            code='repeated_player_in_round',
                            params={
                                'player': player,
                                'group1': player_map[player],
                                'group2': group_num,
                                'round': round_num,
                            },
                        )
                    player_map[player] = group_num
                for i in range(self.instance.group_size - 1):
                    for j in range(i + 1, self.instance.group_size):
                        if group[i] < group[j]:
                            pair = (group[i], group[j])
                        else:
                            pair = (group[j], group[i])
                        if pair in pair_map:
                            raise ValidationError(
                                _('Players %(i)s and %(j)s meet in group %(group)d of round %(round)d but they already met in group %(old_group)d of round %(round)d.'),
                                code='players_meet_more_than_once',
                                params={
                                    'i': group[i],
                                    'j': group[j],
                                    'group': group_num,
                                    'round': round_num,
                                    'group': pair_map[pair]['group_num'],
                                    'round': pair_map[pair]['round_num'],
                                },
                            )
                        pair_map[pair] = {
                            'group_num': group_num,
                            'round_num': round_num,
                        }
        if len(player_set) > self.instance.num_players:
            raise ValidationError(
                _('Too many players in solution; found %(actual)d, expected %(expected)d.'),
                code='too_many_players',
                params={
                    'actual': len(player_set),
                    'expected': self.instance.num_players,
                },
            )

    @property
    def solution(self):
        """
        Returns the solution as a nested array (rounds of groups of players)
        """
        if not self._solution:
            self._solution = [[[int(player) for player in group.split(',')] for group in round.split('|')] for round in self.solution_string.split('\n')]
        return self._solution

    @solution.setter
    def solution(self, array):
        self._solution = array
        self.solution_string = '\n'.join(['|'.join([','.join([str(player) for player in group]) for group in round]) for round in array])

