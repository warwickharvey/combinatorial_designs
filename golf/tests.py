from django.core.exceptions import ValidationError
from django.test import TestCase

import models

# TODO: Override the setUp() or setUpClass() methods to define some
# users/citations/submission_infos to use in the tests, rather than
# defining & using the following methods?

def make_dummy_user():
    """
    Make a User record when we don't care about the contents
    """
    # TODO: Randomise this so that not all records are the same
    user = models.User(name='Foo Bar', email='foo@bar.baz')
    user.save()
    return user

def make_dummy_citation():
    """
    Make a Citation record when we don't care about the contents
    """
    # TODO: Randomise this so that not all records are the same
    citation = models.Citation(citation='Foo N. Bar, My Results, Journal of Baz, 2013')
    citation.save()
    return citation

def make_dummy_submission_info():
    """
    Make a SubmissionInfo record when we don't care about the contents
    """
    citation = make_dummy_citation()
    submitter = make_dummy_user()
    submission_info = models.SubmissionInfo(citation=citation, submitter=submitter)
    submission_info.save()
    return submission_info


class GolfInstanceMethodTests(TestCase):

    ##
    ## Validation tests
    ## 

    def test_group_size_bigger_than_num_groups(self):
        """
        Should not be able to create an instance with a larger group size than
        number of groups (these instances are trivial - exactly one round is
        possible)
        """
        with self.assertRaises(ValidationError):
            instance_4x5 = models.GolfInstance(num_groups=4, group_size=5)
            instance_4x5.save()

    def test_small_num_groups(self):
        """
        Should not be able to create an instance with less than 2 groups
        """
        self.assertRaises(ValidationError, models.GolfInstance, num_groups=1, group_size=4)

    def test_small_group_size(self):
        """
        Should not be able to create an instance with a group size smaller than
        2
        """
        self.assertRaises(ValidationError, models.GolfInstance, num_groups=5, group_size=1)

    def test_valid_instances(self):
        """
        Should be able to create instances with at least two groups of size at
        least two, where the group size does not exceed the number of groups
        """
        instance_2x2 = models.GolfInstance(num_groups=2, group_size=2)
        instance_2x2.save()
        self.assertIsNotNone(instance_2x2)
        instance_20x2 = models.GolfInstance(num_groups=20, group_size=2)
        instance_20x2.save()
        self.assertIsNotNone(instance_20x2)
        instance_20x20 = models.GolfInstance(num_groups=20, group_size=20)
        instance_20x20.save()
        self.assertIsNotNone(instance_20x20)


    ##
    ## Name tests
    ## 

    def test_name_for_instance(self):
        """
        name() should return a suitable human-readable name for an instance
        """
        instance_3x2 = models.GolfInstance(num_groups=3, group_size=2)
        instance_3x2.save()
        self.assertEqual(instance_3x2.name(), '3x2')
        instance_8x4 = models.GolfInstance(num_groups=8, group_size=4)
        instance_8x4.save()
        self.assertEqual(instance_8x4.name(), '8x4')


    ##
    ## Number of players tests
    ## 

    def test_num_players_for_instance(self):
        """
        num_players() should return the right number of players for an instance
        """
        instance_3x2 = models.GolfInstance(num_groups=3, group_size=2)
        instance_3x2.save()
        self.assertEqual(instance_3x2.num_players(), 6)
        instance_8x4 = models.GolfInstance(num_groups=8, group_size=4)
        instance_8x4.save()
        self.assertEqual(instance_8x4.num_players(), 32)


    ##
    ## Upper bound tests
    ## 

    def test_undefined_upper_bound(self):
        """
        upper_bound() should return a dummy bound if no upper bound defined for
        an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertEqual(type(instance_5x4.upper_bound()), models.DummyBound)

    def test_upper_bound_with_single_bound(self):
        """
        upper_bound() should return the bound when only one defined for an
        instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        upper_bound_5x4 = models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        )
        upper_bound_5x4.save()
        self.assertEqual(instance_5x4.upper_bound().num_rounds, 5)

    def test_upper_bound_with_multiple_bounds(self):
        """
        upper_bound() should return the lowest bound when multiple bounds are
        defined for an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=6,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=7,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertEqual(instance_5x4.upper_bound().num_rounds, 5)


    ##
    ## Lower bound tests
    ## 

    def test_undefined_lower_bound(self):
        """
        lower_bound() should return a dummy bound if no lower bound defined for
        an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertEqual(type(instance_5x4.lower_bound()), models.DummyBound)

    def test_lower_bound_with_single_bound(self):
        """
        lower_bound() should return the bound when only one defined for an
        instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        lower_bound_5x4 = models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        )
        lower_bound_5x4.save()
        self.assertEqual(instance_5x4.lower_bound().num_rounds, 5)

    def test_lower_bound_with_multiple_bounds(self):
        """
        lower_bound() should return the highest bound when multiple bounds are
        defined for an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=3,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertEqual(instance_5x4.lower_bound().num_rounds, 5)

    def test_solution_for_undefined_lower_bound(self):
        """
        solution() should return None if no lower bound defined for
        an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        self.assertIsNone(instance_5x4.solution())


    ##
    ## Solution tests
    ## 

    def test_no_solution_for_undefined_lower_bound(self):
        """
        solution() should return None if no lower bound defined for
        an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertIsNone(instance_5x4.solution())

    def test_no_solution_when_only_lower_bounds(self):
        """
        solution() should return None if only lower bounds (not solutions) are
        defined for an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertIsNone(instance_5x4.solution())

    def test_no_solution_when_lower_bound_is_better(self):
        """
        solution() should return None if a lower bound (not solution) for an
        instance is better than the best solution
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
            solution='solution 4',
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertIsNone(instance_5x4.solution())

    def test_solution_when_matching_lower_bounds(self):
        """
        solution() should return a solution if a solution is among the best
        lower bounds for an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertIsNotNone(instance_5x4.solution())
        self.assertEqual(instance_5x4.solution().solution, 'solution 5')

    def test_solution_with_multiple_solutions(self):
        """
        solution() should return the solution with the highest bound when
        multiple solutions are defined for an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=3,
            submission_info=make_dummy_submission_info(),
            solution='solution 3',
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
            solution='solution 4',
        ).save()
        self.assertIsNotNone(instance_5x4.solution())
        self.assertEqual(instance_5x4.solution().num_rounds, 5)
        self.assertEqual(instance_5x4.solution().solution, 'solution 5')


    ##
    ## Closed instance tests
    ## 

    def test_closed_for_undefined_bounds(self):
        """
        is_closed() should return False if no bounds defined for an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_upper_bound(self):
        """
        is_closed() should return False if only an upper bound is defined for
        an instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_lower_bound(self):
        """
        is_closed() should return False if only a lower bound is defined for an
        instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_solution(self):
        """
        is_closed() should return False if only a solution is defined for an
        instance
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_bounds_match(self):
        """
        is_closed() should return True if upper and lower bounds are defined
        for an instance and the bounds match
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertTrue(instance_5x4.is_closed())

    def test_closed_when_bounds_match_with_solution(self):
        """
        is_closed() should return True if an upper bound and a solution are
        defined for an instance and the bounds match
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        self.assertTrue(instance_5x4.is_closed())

    def test_closed_when_bounds_dont_match(self):
        """
        is_closed() should return False if upper and lower bounds are defined
        for an instance but the bounds don't match
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_bounds_dont_match_with_solution(self):
        """
        is_closed() should return False if an upper bound and a solution are
        defined for an instance but the bounds don't match
        """
        instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
            solution='solution 4',
        ).save()
        self.assertFalse(instance_5x4.is_closed())


class GolfLowerBoundMethodTests(TestCase):

    def setUp(self):
        self.instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        self.instance_5x4.save()

    def test_as_solution_when_just_bound(self):
        """
        as_solution() should return None if the bound is just a bound and does
        not have a corresponding GolfSolution
        """
        lower_bound_5x4 = models.GolfLowerBound(
            instance=self.instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        )
        lower_bound_5x4.save()
        self.assertIsNone(lower_bound_5x4.as_solution())

    def test_as_solution_when_solution_exists(self):
        """
        as_solution() should return the corresponding GolfSolution when it
        exists
        """
        models.GolfSolution(
            instance=self.instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        lower_bound_5x4 = models.GolfLowerBound.objects.all()[0]
        solution = lower_bound_5x4.as_solution()
        self.assertIsNotNone(solution)
        self.assertEqual(solution.solution, 'solution 5')



class GolfSolutionMethodTests(TestCase):

    def setUp(self):
        self.instance_5x4 = models.GolfInstance(num_groups=5, group_size=4)
        self.instance_5x4.save()

    def test_as_solution(self):
        """
        as_solution() should return the object itself
        """
        solution_5x4 = models.GolfSolution(
            instance=self.instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution='solution 5',
        )
        solution_5x4.save()
        solution = solution_5x4.as_solution()
        self.assertIsNotNone(solution)
        self.assertIs(solution, solution_5x4)

