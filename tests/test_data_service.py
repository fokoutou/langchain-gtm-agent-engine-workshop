import unittest

from gtm_agent import data_service


class UpdateProspectInfoTests(unittest.TestCase):
    prospect_id = "LEAD-12853"

    def setUp(self):
        self.record = data_service.PROSPECTS[self.prospect_id]
        self.original_tech_stack = list(self.record["tech_stack"])
        self.original_profile = data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        self.record["tech_stack"] = self.original_tech_stack
        data_service._PROFILES.pop(self.prospect_id, None)
        if self.original_profile is not None:
            data_service._PROFILES[self.prospect_id] = self.original_profile

    def test_update_persists_technology_and_preserves_response_shape(self):
        technology = "Test Warehouse"

        result = data_service.update_prospect_info(self.prospect_id, technology)

        self.assertEqual(
            result,
            {
                "updated": True,
                "found": True,
                "tech_stack": self.original_tech_stack + [technology],
            },
        )
        self.assertIn(technology, data_service.fetch_tech_stack(self.prospect_id))

    def test_update_refreshes_cached_profile_tech_stack(self):
        technology = "Test Warehouse"
        data_service._PROFILES[self.prospect_id] = {
            "prospect_id": self.prospect_id,
            "tech_stack": list(self.original_tech_stack),
        }

        data_service.update_prospect_info(self.prospect_id, technology)

        profile = data_service.get_profile_from_db(self.prospect_id)["prospect_profile"]
        self.assertIn(technology, profile["tech_stack"])
        self.assertEqual(profile["tech_stack"], data_service.fetch_tech_stack(self.prospect_id))

    def test_update_preserves_not_found_response(self):
        result = data_service.update_prospect_info("missing-prospect", "Test Warehouse")

        self.assertEqual(result, {"updated": False, "found": False})


if __name__ == "__main__":
    unittest.main()
