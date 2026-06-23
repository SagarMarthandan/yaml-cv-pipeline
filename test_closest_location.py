"""
Unit tests for closest_location.py
"""
import unittest
from closest_location import haversine, find_closest_candidate


class TestHaversine(unittest.TestCase):
    """Test the haversine distance calculation."""

    def test_haversine_same_location(self):
        """Distance between same coordinates should be 0."""
        coord = (52.5200, 13.4050)  # Berlin
        distance = haversine(coord, coord)
        self.assertAlmostEqual(distance, 0, places=2)

    def test_haversine_berlin_munich(self):
        """Test distance between Berlin and Munich."""
        berlin = (52.5200, 13.4050)
        munich = (48.1351, 11.5820)
        distance = haversine(berlin, munich)
        # Berlin to Munich is approximately 504 km
        self.assertAlmostEqual(distance, 504, delta=10)

    def test_haversine_kiel_frankfurt(self):
        """Test distance between Kiel and Frankfurt."""
        kiel = (54.3233, 10.1228)
        frankfurt = (50.1109, 8.6821)
        distance = haversine(kiel, frankfurt)
        # Kiel to Frankfurt is approximately 470 km
        self.assertAlmostEqual(distance, 470, delta=10)


class TestFindClosestCandidate(unittest.TestCase):
    """Test the closest candidate city finder."""

    def test_munich_to_frankfurt(self):
        """Munich should map to Frankfurt."""
        result = find_closest_candidate("Munich")
        self.assertEqual(result, "Frankfurt, Germany")

    def test_munich_german_to_frankfurt(self):
        """München (German) should map to Frankfurt."""
        result = find_closest_candidate("München")
        self.assertEqual(result, "Frankfurt, Germany")

    def test_stuttgart_to_frankfurt(self):
        """Stuttgart should map to Frankfurt."""
        result = find_closest_candidate("Stuttgart")
        self.assertEqual(result, "Frankfurt, Germany")

    def test_frankfurt_to_frankfurt(self):
        """Frankfurt should map to Frankfurt."""
        result = find_closest_candidate("Frankfurt")
        self.assertEqual(result, "Frankfurt, Germany")

    def test_frankfurt_am_main_to_frankfurt(self):
        """Frankfurt am Main should map to Frankfurt."""
        result = find_closest_candidate("Frankfurt am Main")
        self.assertEqual(result, "Frankfurt, Germany")

    def test_berlin_to_berlin(self):
        """Berlin should map to Berlin."""
        result = find_closest_candidate("Berlin")
        self.assertEqual(result, "Berlin, Germany")

    def test_dresden_to_berlin(self):
        """Dresden should map to Berlin."""
        result = find_closest_candidate("Dresden")
        self.assertEqual(result, "Berlin, Germany")

    def test_leipzig_to_berlin(self):
        """Leipzig should map to Berlin."""
        result = find_closest_candidate("Leipzig")
        self.assertEqual(result, "Berlin, Germany")

    def test_koln_to_koln(self):
        """Köln should map to Köln."""
        result = find_closest_candidate("Köln")
        self.assertEqual(result, "Köln, Germany")

    def test_cologne_to_koln(self):
        """Cologne (English) should map to Köln."""
        result = find_closest_candidate("Cologne")
        self.assertEqual(result, "Köln, Germany")

    def test_dusseldorf_to_koln(self):
        """Düsseldorf should map to Köln."""
        result = find_closest_candidate("Düsseldorf")
        self.assertEqual(result, "Köln, Germany")

    def test_bonn_to_koln(self):
        """Bonn should map to Köln."""
        result = find_closest_candidate("Bonn")
        self.assertEqual(result, "Köln, Germany")

    def test_aachen_to_koln(self):
        """Aachen should map to Köln."""
        result = find_closest_candidate("Aachen")
        self.assertEqual(result, "Köln, Germany")

    def test_hamburg_to_kiel(self):
        """Hamburg should map to Kiel."""
        result = find_closest_candidate("Hamburg")
        self.assertEqual(result, "Kiel, Germany")

    def test_kiel_to_kiel(self):
        """Kiel should map to Kiel."""
        result = find_closest_candidate("Kiel")
        self.assertEqual(result, "Kiel, Germany")

    def test_lubeck_to_kiel(self):
        """Lübeck should map to Kiel."""
        result = find_closest_candidate("Lübeck")
        self.assertEqual(result, "Kiel, Germany")

    def test_remote_to_kiel(self):
        """Remote/Work from home should default to Kiel."""
        result = find_closest_candidate("Remote")
        self.assertEqual(result, "Kiel, Germany")

    def test_home_office_to_kiel(self):
        """Home Office should default to Kiel."""
        result = find_closest_candidate("Home Office")
        self.assertEqual(result, "Kiel, Germany")

    def test_germany_wide_to_kiel(self):
        """Germany-wide should default to Kiel."""
        result = find_closest_candidate("Germany-wide")
        self.assertEqual(result, "Kiel, Germany")

    def test_deutschlandweit_to_kiel(self):
        """Deutschlandweit should default to Kiel."""
        result = find_closest_candidate("Deutschlandweit")
        self.assertEqual(result, "Kiel, Germany")

    def test_unknown_city_to_kiel(self):
        """Unknown city should default to Kiel."""
        result = find_closest_candidate("UnknownCityName")
        self.assertEqual(result, "Kiel, Germany")

    def test_empty_string_to_kiel(self):
        """Empty string should default to Kiel."""
        result = find_closest_candidate("")
        self.assertEqual(result, "Kiel, Germany")


if __name__ == '__main__':
    unittest.main()
