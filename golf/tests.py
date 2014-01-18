import pprint

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

import models
import constructions

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

def make_instance(num_groups, group_size):
    """
    Make (and save) a GolfInstance with the given parameters
    """
    instance = models.GolfInstance(num_groups=num_groups, group_size=group_size)
    instance.save()
    return instance


solution_string_4x3_4="""
0,1,2|3,4,5|6,7,8|9,10,11
0,3,6|1,4,9|2,7,10|5,8,11
0,8,9|1,3,7|2,4,11|5,6,10
0,4,10|1,6,11|2,3,8|5,7,9
""".strip()

solution_string_5x4_5="""
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|5,12,14,17
1,8,12,16|2,11,14,19|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip()

solution_string_5x4_3 = '\n'.join(solution_string_5x4_5.split()[:3])
solution_string_5x4_4 = '\n'.join(solution_string_5x4_5.split()[:4])


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
            instance_4x5 = make_instance(4, 5)

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
        instance_2x2 = make_instance(2, 2)
        self.assertIsNotNone(instance_2x2)
        instance_20x2 = make_instance(20, 2)
        self.assertIsNotNone(instance_20x2)
        instance_20x20 = make_instance(20, 20)
        self.assertIsNotNone(instance_20x20)


    ##
    ## Name tests
    ## 

    def test_name_for_instance(self):
        """
        name() should return a suitable human-readable name for an instance
        """
        instance_3x2 = make_instance(3, 2)
        self.assertEqual(instance_3x2.name(), '3x2')
        instance_8x4 = make_instance(8, 4)
        self.assertEqual(instance_8x4.name(), '8x4')


    ##
    ## Number of players tests
    ## 

    def test_num_players_for_instance(self):
        """
        num_players should return the right number of players for an instance
        """
        instance_3x2 = make_instance(3, 2)
        self.assertEqual(instance_3x2.num_players, 6)
        instance_8x4 = make_instance(8, 4)
        self.assertEqual(instance_8x4.num_players, 32)


    ##
    ## Upper bound tests
    ## 

    def test_undefined_upper_bound(self):
        """
        upper_bound should return a dummy bound if no upper bound defined for
        an instance
        """
        instance_5x4 = make_instance(5, 4)
        self.assertEqual(type(instance_5x4.upper_bound), models.DummyBound)

    def test_upper_bound_with_single_bound(self):
        """
        upper_bound should return the bound when only one defined for an
        instance
        """
        instance_5x4 = make_instance(5, 4)
        upper_bound_5x4 = models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        )
        upper_bound_5x4.save()
        self.assertEqual(instance_5x4.upper_bound.num_rounds, 5)

    def test_upper_bound_with_multiple_bounds(self):
        """
        upper_bound should return the lowest bound when multiple bounds are
        defined for an instance
        """
        instance_5x4 = make_instance(5, 4)
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
        self.assertEqual(instance_5x4.upper_bound.num_rounds, 5)


    ##
    ## Lower bound tests
    ## 

    def test_undefined_lower_bound(self):
        """
        lower_bound should return a dummy bound if no lower bound defined for
        an instance
        """
        instance_5x4 = make_instance(5, 4)
        self.assertEqual(type(instance_5x4.lower_bound), models.DummyBound)

    def test_lower_bound_with_single_bound(self):
        """
        lower_bound should return the bound when only one defined for an
        instance
        """
        instance_5x4 = make_instance(5, 4)
        lower_bound_5x4 = models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        )
        lower_bound_5x4.save()
        self.assertEqual(instance_5x4.lower_bound.num_rounds, 5)

    def test_lower_bound_with_multiple_bounds(self):
        """
        lower_bound should return the highest bound when multiple bounds are
        defined for an instance
        """
        instance_5x4 = make_instance(5, 4)
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
        self.assertEqual(instance_5x4.lower_bound.num_rounds, 5)

    def test_solution_for_undefined_lower_bound(self):
        """
        solution() should return None if no lower bound defined for
        an instance
        """
        instance_5x4 = make_instance(5, 4)
        self.assertIsNone(instance_5x4.solution())


    ##
    ## Solution tests
    ## 

    def test_no_solution_for_undefined_lower_bound(self):
        """
        solution() should return None if no lower bound defined for
        an instance
        """
        instance_5x4 = make_instance(5, 4)
        self.assertIsNone(instance_5x4.solution())

    def test_no_solution_when_only_lower_bounds(self):
        """
        solution() should return None if only lower bounds (not solutions) are
        defined for an instance
        """
        instance_5x4 = make_instance(5, 4)
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
        instance_5x4 = make_instance(5, 4)
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_4,
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
        instance_5x4 = make_instance(5, 4)
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_5,
        ).save()
        models.GolfLowerBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        self.assertIsNotNone(instance_5x4.solution())
        self.assertEqual(instance_5x4.solution().solution_string, solution_string_5x4_5)

    def test_solution_with_multiple_solutions(self):
        """
        solution() should return the solution with the highest bound when
        multiple solutions are defined for an instance
        """
        instance_5x4 = make_instance(5, 4)
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=3,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_3,
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_5,
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_4,
        ).save()
        self.assertIsNotNone(instance_5x4.solution())
        self.assertEqual(instance_5x4.solution().num_rounds, 5)
        self.assertEqual(instance_5x4.solution().solution_string, solution_string_5x4_5)


    ##
    ## Closed instance tests
    ## 

    def test_closed_for_undefined_bounds(self):
        """
        is_closed() should return False if no bounds defined for an instance
        """
        instance_5x4 = make_instance(5, 4)
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_only_upper_bound(self):
        """
        is_closed() should return False if only an upper bound is defined for
        an instance
        """
        instance_5x4 = make_instance(5, 4)
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
        instance_5x4 = make_instance(5, 4)
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
        instance_5x4 = make_instance(5, 4)
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_5,
        ).save()
        self.assertFalse(instance_5x4.is_closed())

    def test_closed_when_bounds_match(self):
        """
        is_closed() should return True if upper and lower bounds are defined
        for an instance and the bounds match
        """
        instance_5x4 = make_instance(5, 4)
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
        instance_5x4 = make_instance(5, 4)
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_5,
        ).save()
        self.assertTrue(instance_5x4.is_closed())

    def test_closed_when_bounds_dont_match(self):
        """
        is_closed() should return False if upper and lower bounds are defined
        for an instance but the bounds don't match
        """
        instance_5x4 = make_instance(5, 4)
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
        instance_5x4 = make_instance(5, 4)
        models.GolfUpperBound(
            instance=instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
        ).save()
        models.GolfSolution(
            instance=instance_5x4,
            num_rounds=4,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_4,
        ).save()
        self.assertFalse(instance_5x4.is_closed())


class GolfLowerBoundMethodTests(TestCase):

    def setUp(self):
        self.instance_5x4 = make_instance(5, 4)

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
            solution_string=solution_string_5x4_5,
        ).save()
        lower_bound_5x4 = models.GolfLowerBound.objects.all()[0]
        solution = lower_bound_5x4.as_solution()
        self.assertIsNotNone(solution)
        self.assertEqual(solution.solution_string, solution_string_5x4_5)


class GolfSolutionMethodTests(TestCase):

    def setUp(self):
        self.instance_4x3 = make_instance(4, 3)
        self.instance_5x4 = make_instance(5, 4)

    def check_solution_validation(self, code, instance, num_rounds, solution_string):
        solution = models.GolfSolution(
            instance=instance,
            num_rounds=num_rounds,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string,
        )
        with self.assertRaises(ValidationError):
            try:
                solution.save()
            except ValidationError as e:
                self.assertIn(code, [x.code for x in e.error_dict['__all__']])
                raise

    def test_as_solution(self):
        """
        as_solution() should return the object itself
        """
        solution_5x4 = models.GolfSolution(
            instance=self.instance_5x4,
            num_rounds=5,
            submission_info=make_dummy_submission_info(),
            solution_string=solution_string_5x4_5,
        )
        solution_5x4.save()
        solution = solution_5x4.as_solution()
        self.assertIsNotNone(solution)
        self.assertIs(solution, solution_5x4)

    def test_validate_not_enough_rounds(self):
        """
        validate_solution_string() should raise a ValidationError if the
        solution does not have enough rounds
        """
        self.check_solution_validation(
            'wrong_number_of_rounds',
            self.instance_5x4,
            5,
            solution_string_5x4_4,
        )

    def test_validate_too_many_rounds(self):
        """
        validate_solution_string() should raise a ValidationError if the
        solution has too many rounds
        """
        self.check_solution_validation(
            'wrong_number_of_rounds',
            self.instance_5x4,
            4,
            solution_string_5x4_5,
        )

    def test_validate_not_enough_groups(self):
        """
        validate_solution_string() should raise a ValidationError if a round in
        the solution does not have enough groups
        """
        self.check_solution_validation(
            'wrong_number_of_groups_in_round',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18
1,8,12,16|2,11,14,19|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip(),
        )

    def test_validate_too_many_groups(self):
        """
        validate_solution_string() should raise a ValidationError if a round in
        the solution has too many groups
        """
        self.check_solution_validation(
            'wrong_number_of_groups_in_round',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|5,12,14,17
1,8,12,16|2,11|14,19|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip(),
        )

    def test_validate_not_enough_players_in_group(self):
        """
        validate_solution_string() should raise a ValidationError if a group in
        the solution does not have enough players
        """
        self.check_solution_validation(
            'wrong_number_of_players_in_group',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|5,12,14,17
1,8,12,16|2,11,14|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip(),
        )

    def test_validate_too_many_players_in_group(self):
        """
        validate_solution_string() should raise a ValidationError if a group in
        the solution has too many players
        """
        self.check_solution_validation(
            'wrong_number_of_players_in_group',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|5,12,14,17
1,8,12,16|2,11,14,19,21|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip(),
        )

    def test_validate_player_appearing_twice_in_round(self):
        """
        validate_solution_string() should raise a ValidationError if a player
        appears more than once in a round
        """
        self.check_solution_validation(
            'repeated_player_in_round',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|7,12,14,17
1,8,12,16|2,11,14,19|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip(),
        )

    def test_validate_pair_appearing_twice_in_solution(self):
        """
        validate_solution_string() should raise a ValidationError if a pair of
        players appears more than once in a solution
        """
        self.check_solution_validation(
            'players_meet_more_than_once',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,17|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|5,12,14,17
1,8,12,16|2,11,14,19|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,19|8,9,15,20
""".strip(),
        )

    def test_too_many_players_in_solution(self):
        """
        validate_solution_string() should raise a ValidationError if a pair of
        players appears more than once in a solution
        """
        self.check_solution_validation(
            'too_many_players',
            self.instance_5x4,
            5,
            """
1,2,3,4|5,6,7,8|9,10,11,12|13,14,15,16|17,18,19,20
1,5,9,13|2,10,15,21|3,8,14,20|4,7,12,19|6,11,16,18
1,7,11,15|2,9,16,20|3,6,13,19|4,8,10,18|5,12,14,17
1,8,12,16|2,11,14,19|3,5,15,18|4,6,9,17|7,10,13,20
1,6,10,14|2,12,13,18|3,7,16,17|4,5,11,20|8,9,15,19
""".strip(),
        )


class ConstructorMethodTests(TestCase):

    def construct(self, num_groups, group_size):
        """
        Run the constructor's construct() method on the instance with the given
        parameters
        """
        instance = make_instance(num_groups, group_size)
        return self.constructor.construct(instance)


class TrivialSolutionConstructorMethodTests(ConstructorMethodTests):

    def setUp(self):
        self.constructor = constructions.TrivialSolutionConstructor()

    def do_test(self, num_groups, group_size):
        """
        TrivialSolutionConstructor.construct() should return a lower bound of 2
        for the instance with the given parameters
        """
        construction = self.construct(num_groups, group_size)
        self.assertIsInstance(construction, models.GolfSolution)
        self.assertEqual(construction.num_rounds, 2)

    def test_construct(self):
        """
        construct() should make 2-round solutions for various instances
        """
        self.do_test(2, 2)
        self.do_test(5, 4)
        self.do_test(6, 6)
        self.do_test(8, 4)
        self.do_test(8, 5)
        self.do_test(8, 8)


class TrivialUpperBoundConstructorMethodTests(ConstructorMethodTests):

    def setUp(self):
        self.constructor = constructions.TrivialUpperBoundConstructor()

    def do_test(self, num_groups, group_size, num_rounds):
        """
        TrivialUpperBoundConstructor.construct() should return the given upper
        bound for the instance with the given parameters
        """
        construction = self.construct(num_groups, group_size)
        self.assertIsInstance(construction, models.GolfUpperBound)
        self.assertEqual(construction.num_rounds, num_rounds)

    def test_construct(self):
        """
        construct() should make suitable upper bounds for various instances
        """
        self.do_test(2, 2, 3)
        self.do_test(5, 4, 6)
        self.do_test(6, 6, 7)
        self.do_test(7, 4, 9)
        self.do_test(8, 4, 10)
        self.do_test(8, 5, 9)
        self.do_test(8, 8, 9)


class ConstructorsMethodTests(ConstructorMethodTests):

    def setUp(self):
        self.constructors = constructions.Constructors()

    def check_instance_in_instances(self, num_groups, group_size, instances):
        """
        Check that the instance with the given parameters appears in the given
        list of instances
        """
        self.assertIn(models.GolfInstance.objects.get(num_groups=num_groups, group_size=group_size), instances)

    def check_instance_in_bounds(self, num_groups, group_size, bounds):
        """
        Check that the given list of bounds contains an entry corresponding to
        the instance with the given parameters
        """
        instance = models.GolfInstance.objects.get(num_groups=num_groups, group_size=group_size)
        bounds.get(instance=instance)

    def test_instances(self):
        """
        instances() should make and return a suitable set of instances
        """
        instances = self.constructors.instances
        self.check_instance_in_instances(2, 2, instances)
        self.check_instance_in_instances(20, 2, instances)
        self.check_instance_in_instances(20, 20, instances)

    def test_instances_existing_instances(self):
        """
        instances() should return rather than create any existing instances
        """
        instance_3x2 = make_instance(3, 2)
        instance_5x4 = make_instance(5, 4)
        instance_8x4 = make_instance(8, 4)
        instances = self.constructors.instances
        self.assertIn(instance_3x2, instances)
        self.assertIn(instance_5x4, instances)
        self.assertIn(instance_8x4, instances)
        # Check some other instances are still created
        self.check_instance_in_instances(2, 2, instances)
        self.check_instance_in_instances(20, 2, instances)
        self.check_instance_in_instances(20, 20, instances)

    def test_instances_already_run(self):
        """
        instances() should return the same instances if it's already been run
        """
        instances = self.constructors.instances
        self.assertIs(self.constructors.instances, instances)

    def test_instances_another_copy_already_run(self):
        """
        instances() should return the same instances as another instance of the
        class
        """
        instances = self.constructors.instances
        instances2 = constructions.Constructors().instances
        self.assertEqual(instances, instances2)

    def check_all_constructions(self):
        """
        Check that solutions/bounds have been created by the various
        constructors
        """
        trivial_solutions = models.GolfBound.objects.filter(submission_info__construction__id='golf_trivial_solution_constructor')
        self.assertEqual(len(trivial_solutions), len(self.constructors.instances))
        self.check_instance_in_bounds(2, 2, trivial_solutions)
        self.check_instance_in_bounds(20, 2, trivial_solutions)
        self.check_instance_in_bounds(20, 20, trivial_solutions)
        self.check_instance_in_bounds(20, 20, trivial_solutions)

        trivial_bounds = models.GolfBound.objects.filter(submission_info__construction__id='golf_trivial_upper_bound_constructor')
        self.assertEqual(len(trivial_bounds), len(self.constructors.instances))
        self.check_instance_in_bounds(2, 2, trivial_bounds)
        self.check_instance_in_bounds(20, 2, trivial_bounds)
        self.check_instance_in_bounds(20, 20, trivial_bounds)

    def test_construct_all(self):
        """
        Check that calling construct_all() results in solutions/bounds being
        created by the various constructors
        """
        self.constructors.construct_all()
        self.check_all_constructions()

    def test_construct_all_twice(self):
        """
        Check that calling construct_all() twice does not result in two copies
        of the constructions
        """
        self.constructors.construct_all()
        self.constructors.construct_all()
        self.check_all_constructions()


class GolfIndexViewTests(TestCase):
    def setUp(self):
        constructions.Constructors().construct_all()

    def check_instance_in_context(self, num_groups, group_size, context):
        """
        Check that the given context contains an entry corresponding to the
        instance with the given parameters
        """
        instance = models.GolfInstance.objects.get(num_groups=num_groups, group_size=group_size)
        self.assertIn(instance, context['instance_list'])

    def test_index_view(self):
        """
        Check that the index view works and contains some instances
        """
        response = self.client.get(reverse('golf:index'))
        self.assertEqual(response.status_code, 200)
        self.check_instance_in_context(2, 2, response.context)
        self.check_instance_in_context(20, 2, response.context)
        self.check_instance_in_context(20, 20, response.context)

    def test_index_view_sorted(self):
        """
        Check that the index view has the instances sorted by group size and
        then number of groups
        """
        response = self.client.get(reverse('golf:index'))
        instances = response.context['instance_list']
        previous_instance = instances[0]
        for instance in instances[1:]:
            self.assertGreaterEqual(instance.group_size, previous_instance.group_size)
            if instance.group_size == previous_instance.group_size:
                self.assertGreaterEqual(instance.num_groups, previous_instance.num_groups)
            previous_instance = instance

    def test_index_view_bounds(self):
        """
        Check that the index view has correct bounds for the group size and
        number of groups
        """
        response = self.client.get(reverse('golf:index'))
        self.assertIn('group_size__min', response.context)
        self.assertIn('group_size__max', response.context)
        self.assertIn('num_groups__min', response.context)
        self.assertIn('num_groups__max', response.context)
        instances = response.context['instance_list']
        for instance in instances:
            self.assertGreaterEqual(instance.group_size, response.context['group_size__min'])
            self.assertLessEqual(instance.group_size, response.context['group_size__max'])
            self.assertGreaterEqual(instance.num_groups, response.context['num_groups__min'])
            self.assertLessEqual(instance.num_groups, response.context['num_groups__max'])

