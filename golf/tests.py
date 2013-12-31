from django.test import TestCase

from golf.models import User, Citation, SubmissionInfo
from golf.models import GolfInstance, GolfSolution
from golf.models import DummyBound, GolfUpperBound, GolfLowerBound

class GolfInstanceMethodTests(TestCase):

    # TODO: Override the setUp() or setUpClass() methods to define some
    # users/citations/submission_infos to use in the tests, rather than
    # defining & using the following methods?

    def make_dummy_user(self):
        """
        Make a User record when we don't care about the contents
        """
        # TODO: Randomise this so that not all records are the same
        user = User(name='Foo Bar', email='foo@bar.baz')
        user.save()
        return user

    def make_dummy_citation(self):
        """
        Make a Citation record when we don't care about the contents
        """
        # TODO: Randomise this so that not all records are the same
        citation = Citation(citation='Foo N. Bar, My Results, Journal of Baz, 2013')
        citation.save()
        return citation

    def make_dummy_submission_info(self):
        """
        Make a SubmissionInfo record when we don't care about the contents
        """
        citation = self.make_dummy_citation()
        submitter = self.make_dummy_user()
        submission_info = SubmissionInfo(citation=citation, submitter=submitter)
        submission_info.save()
        return submission_info


    ##
    ## Name tests
    ## 

    def test_name_for_instance(self):
        """
        name() should return a suitable human-readable name for an instance
        """
        instance_3x2 = GolfInstance(num_groups=3, group_size=2)
        instance_3x2.save()
        self.assertEqual(instance_3x2.name(), '3x2')
        instance_8x4 = GolfInstance(num_groups=8, group_size=4)
        instance_8x4.save()
        self.assertEqual(instance_8x4.name(), '8x4')


    ##
    ## Number of players tests
    ## 

    def test_num_players_for_instance(self):
        """
        num_players() should return the right number of players for an instance
        """
        instance_3x2 = GolfInstance(num_groups=3, group_size=2)
        instance_3x2.save()
        self.assertEqual(instance_3x2.num_players(), 6)
        instance_8x4 = GolfInstance(num_groups=8, group_size=4)
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
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertEqual(type(instance_5x4.upper_bound()), DummyBound)

    def test_upper_bound_with_single_bound(self):
        """
        upper_bound() should return the bound when only one defined for an
        instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        upper_bound_5x4 = GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        )
        upper_bound_5x4.save()
        self.assertEqual(instance_5x4.upper_bound().num_rounds, 5)

    def test_upper_bound_with_multiple_bounds(self):
        """
        upper_bound() should return the lowest bound when multiple bounds are
        defined for an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=6,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=7,
            submission_info=self.make_dummy_submission_info(),
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
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertEqual(type(instance_5x4.lower_bound()), DummyBound)

    def test_lower_bound_with_single_bound(self):
        """
        lower_bound() should return the bound when only one defined for an
        instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        lower_bound_5x4 = GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        )
        lower_bound_5x4.save()
        self.assertEqual(instance_5x4.lower_bound().num_rounds, 5)

    def test_lower_bound_with_multiple_bounds(self):
        """
        lower_bound() should return the highest bound when multiple bounds are
        defined for an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=3,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertEqual(instance_5x4.lower_bound().num_rounds, 5)

    def test_solution_for_undefined_lower_bound(self):
        """
        solution() should return None if no lower bound defined for
        an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        self.assertIsNone(instance_5x4.solution())


    ##
    ## Solution tests
    ## 

    def test_no_solution_for_undefined_lower_bound(self):
        """
        solution() should return None if no lower bound defined for
        an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertIsNone(instance_5x4.solution())

    def test_no_solution_when_only_lower_bounds(self):
        """
        solution() should return None if only lower bounds (not solutions) are
        defined for an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertIsNone(instance_5x4.solution())

    def test_no_solution_when_lower_bound_is_better(self):
        """
        solution() should return None if a lower bound (not solution) for an
        instance is better than the best solution
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 4',
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertIsNone(instance_5x4.solution())

    def test_solution_when_matching_lower_bounds(self):
        """
        solution() should return a solution if a solution is among the best
        lower bounds for an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertIsNotNone(instance_5x4.solution())
        self.assertEqual(instance_5x4.solution().solution, 'solution 5')

    def test_solution_with_multiple_solutions(self):
        """
        solution() should return the solution with the highest bound when
        multiple solutions are defined for an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=3,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 3',
        ).save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=self.make_dummy_submission_info(),
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
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_upper_bound(self):
        """
        is_closed() should return False if only an upper bound is defined for
        an instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_lower_bound(self):
        """
        is_closed() should return False if only a lower bound is defined for an
        instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_solution(self):
        """
        is_closed() should return False if only a solution is defined for an
        instance
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_bounds_match(self):
        """
        is_closed() should return True if upper and lower bounds are defined
        for an instance and the bounds match
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertTrue(instance_5x4.is_closed())

    def test_closed_when_bounds_match_with_solution(self):
        """
        is_closed() should return True if an upper bound and a solution are
        defined for an instance and the bounds match
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 5',
        ).save()
        self.assertTrue(instance_5x4.is_closed())

    def test_closed_when_bounds_dont_match(self):
        """
        is_closed() should return False if upper and lower bounds are defined
        for an instance but the bounds don't match
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfLowerBound(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_bounds_dont_match_with_solution(self):
        """
        is_closed() should return False if an upper bound and a solution are
        defined for an instance but the bounds don't match
        """
        instance_5x4 = GolfInstance(num_groups=5, group_size=4)
        instance_5x4.save()
        GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=self.make_dummy_submission_info(),
        ).save()
        GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=self.make_dummy_submission_info(),
            solution='solution 4',
        ).save()
        self.assertFalse(instance_5x4.is_closed())

