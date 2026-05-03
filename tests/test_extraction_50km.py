import unittest
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import extraction_50km as extraction


def row(listing_id, price=100000, address=None):
    return {
        "_id": listing_id,
        "Prix": price,
        "Ville": "Sherbrooke",
        "Adresse": address or f"{listing_id} rue Test",
    }


def ref_for(*listing_ids, price=100000):
    return {
        listing_id: {
            "prix": price,
            "ville": "Sherbrooke",
            "adresse": f"{listing_id} rue Test",
        }
        for listing_id in listing_ids
    }


def ref_by_address(*addresses, price=100000, listing_id="10000000"):
    return {
        extraction.address_key(address): {
            "prix": price,
            "ville": "Sherbrooke",
            "adresse": address,
            "listing_id": listing_id,
        }
        for address in addresses
    }


class ChangeDetectionTests(unittest.TestCase):
    def test_detect_changements_tracks_new_removed_and_price_changes_by_address(self):
        rows = [
            row("10000001", price=100000, address="10, Rue King Ouest"),
            row("10000002", price=225000, address="20, Rue Queen"),
            row("10000003", price=300000, address="30, Rue Wellington"),
        ]
        ref = ref_by_address(
            "10, Rue King Ouest",
            "20, Rue Queen",
            "99, Rue Disparue",
            price=100000,
        )

        nouveaux, retires, prix_changes = extraction.detect_changements(rows, ref)

        self.assertEqual(nouveaux, {extraction.address_key("30, Rue Wellington")})
        self.assertEqual(
            {item["id"] for item in retires},
            {extraction.address_key("99, Rue Disparue")},
        )
        self.assertEqual(
            prix_changes,
            {extraction.address_key("20, Rue Queen"): 100000},
        )

    def test_detect_changements_has_no_false_changes_when_address_matches(self):
        rows = [
            row("20000001", address="10, Rue King Ouest"),
            row("20000002", address="20, Rue Queen"),
        ]
        ref = ref_by_address("10, Rue King Ouest", "20, Rue Queen")

        nouveaux, retires, prix_changes = extraction.detect_changements(rows, ref)

        self.assertEqual(nouveaux, set())
        self.assertEqual(retires, [])
        self.assertEqual(prix_changes, {})

    def test_detect_changements_ignores_changed_listing_id_for_same_address(self):
        rows = [row("22222222", price=100000, address="115 - 117, 11e Avenue Nord")]
        ref = ref_by_address(
            "115-117, 11e Avenue Nord",
            price=100000,
            listing_id="11111111",
        )

        nouveaux, retires, prix_changes = extraction.detect_changements(rows, ref)

        self.assertEqual(nouveaux, set())
        self.assertEqual(retires, [])
        self.assertEqual(prix_changes, {})

    def test_detect_changements_tracks_price_change_for_same_address_new_id(self):
        rows = [row("22222222", price=125000, address="115 - 117, 11e Avenue Nord")]
        ref = ref_by_address(
            "115-117, 11e Avenue Nord",
            price=100000,
            listing_id="11111111",
        )

        _nouveaux, _retires, prix_changes = extraction.detect_changements(rows, ref)

        self.assertEqual(
            prix_changes,
            {extraction.address_key("115 - 117, 11e Avenue Nord"): 100000},
        )

    def test_address_key_normalizes_accents_spacing_and_punctuation(self):
        self.assertEqual(
            extraction.address_key("115 - 117, 11e Avenue Nord, Sherbrooke (Fleurimont)"),
            extraction.address_key("115-117  11E avenue nord Sherbrooke (Fleurimont)"),
        )
        self.assertEqual(
            extraction.address_key("170, Rue Murray, Sherbrooke (Fleurimont)"),
            "170 rue murray sherbrooke (fleurimont)",
        )


class SafetyGuardTests(unittest.TestCase):
    def test_rejects_more_than_ten_removed_listings(self):
        rows = [row(str(10000000 + idx)) for idx in range(100)]
        ref = ref_for(*(str(10000000 + idx) for idx in range(100)))
        retires = [{"id": str(20000000 + idx)} for idx in range(11)]

        self.assertFalse(extraction.is_reference_update_safe(rows, ref, retires))

    def test_rejects_more_than_ten_percent_removed_listings(self):
        rows = [row(str(10000000 + idx)) for idx in range(50)]
        ref = ref_for(*(str(10000000 + idx) for idx in range(50)))
        retires = [{"id": str(20000000 + idx)} for idx in range(6)]

        self.assertFalse(extraction.is_reference_update_safe(rows, ref, retires))

    def test_rejects_active_count_drop(self):
        rows = [row(str(10000000 + idx)) for idx in range(89)]
        ref = ref_for(*(str(10000000 + idx) for idx in range(100)))

        self.assertFalse(extraction.is_reference_update_safe(rows, ref, []))

    def test_rejects_incomplete_collection(self):
        rows = [row("10000001")]
        ref = ref_for("10000001")

        self.assertFalse(
            extraction.is_reference_update_safe(
                rows,
                ref,
                [],
                collection_complete=False,
            )
        )

    def test_rejects_missing_extracted_listing(self):
        rows = [row("10000001")]
        ref = ref_for("10000001")

        self.assertFalse(
            extraction.is_reference_update_safe(
                rows,
                ref,
                [],
                expected_listing_count=2,
            )
        )


class PaginationTests(unittest.TestCase):
    def test_build_stable_page_url_defaults_none_sort_to_date_desc(self):
        html = """
        <span id="currentSort">None</span>
        <span id="sortSeed">123456</span>
        <span id="pageSize">20</span>
        <span id="serializedSearchQuery">abc+def</span>
        """

        url = extraction.build_stable_page_url(
            "https://www.centris.ca/fr/plex~a-vendre~sherbrooke",
            html,
            2,
        )

        self.assertIn("sort=DateDesc", url)
        self.assertIn("sortSeed=123456", url)
        self.assertIn("pageSize=20", url)
        self.assertIn("page=2", url)


class ListingCollectionTests(unittest.TestCase):
    def test_collects_absolute_and_relative_listing_urls(self):
        html = """
        <span id="numberOfResults">2</span>
        <a href="https://www.centris.ca/fr/duplex~a-vendre~weedon/20726770">A</a>
        <a href="/fr/triplex~a-vendre~sherbrooke/12345678">B</a>
        """

        with patch.object(extraction, "fetch_response", return_value=(html, 200)):
            results, stats = extraction.get_listing_urls_for_ville(
                "Test",
                "test",
                return_stats=True,
            )

        self.assertEqual(stats, {"expected": 2, "collected": 2, "complete": True})
        self.assertEqual(
            results["20726770"],
            "https://www.centris.ca/fr/duplex~a-vendre~weedon/20726770",
        )
        self.assertEqual(
            results["12345678"],
            "https://www.centris.ca/fr/triplex~a-vendre~sherbrooke/12345678",
        )

    def test_404_city_is_treated_as_empty_not_incomplete(self):
        with patch.object(extraction, "fetch_response", return_value=("", 404)):
            results, stats = extraction.get_listing_urls_for_ville(
                "Missing",
                "missing",
                return_stats=True,
            )

        self.assertEqual(results, {})
        self.assertEqual(stats, {"expected": 0, "collected": 0, "complete": True})

    def test_network_failure_is_incomplete(self):
        with patch.object(extraction, "fetch_response", return_value=("", None)):
            results, stats = extraction.get_listing_urls_for_ville(
                "Broken",
                "broken",
                return_stats=True,
            )

        self.assertEqual(results, {})
        self.assertEqual(stats, {"expected": 0, "collected": 0, "complete": False})


class UnitCountTests(unittest.TestCase):
    def test_unit_count_prefers_raw_count(self):
        count = extraction.resolve_unit_count(
            "https://www.centris.ca/fr/duplex~a-vendre~sherbrooke/12345678",
            "Résidentiel (4)",
            "2 x 3 1/2",
        )

        self.assertEqual(count, 4)

    def test_unit_count_falls_back_to_listing_type(self):
        urls = {
            "duplex": 2,
            "triplex": 3,
            "quadruplex": 4,
            "quintuplex": 5,
        }

        for listing_type, expected in urls.items():
            with self.subTest(listing_type=listing_type):
                count = extraction.resolve_unit_count(
                    f"https://www.centris.ca/fr/{listing_type}~a-vendre~sherbrooke/12345678",
                    "Non indiqué",
                    "Non indiqué",
                )
                self.assertEqual(count, expected)

    def test_unit_count_falls_back_to_clear_unit_mix(self):
        count = extraction.resolve_unit_count(
            "https://www.centris.ca/fr/plex~a-vendre~sherbrooke/12345678",
            "Non indiqué",
            "4 x 3 1/2, 1 x 5 1/2",
        )

        self.assertEqual(count, 5)

    def test_unit_count_ignores_ambiguous_unit_mix(self):
        count = extraction.resolve_unit_count(
            "https://www.centris.ca/fr/plex~a-vendre~sherbrooke/12345678",
            "Non indiqué",
            "3 1/2, 5 1/2",
        )

        self.assertEqual(count, "Non indiqué")


if __name__ == "__main__":
    unittest.main()
