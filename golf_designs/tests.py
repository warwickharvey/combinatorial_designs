from django.test import TestCase

from golf_designs.models import GolfInstance

class GolfInstanceMethodTests(TestCase):

    def test_name_for_instance(self):
        """
        name() should return a suitable human-readable name for an instance
        """
        instance3x2 = GolfInstance(num_groups=3, group_size=2)
        self.assertEqual(instance3x2.name(), '3x2')
        instance8x4 = GolfInstance(num_groups=8, group_size=4)
        self.assertEqual(instance8x4.name(), '8x4')

