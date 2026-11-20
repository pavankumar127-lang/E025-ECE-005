
import unittest
import models
from engine import PooledDataEngine


class TestModels(unittest.TestCase):

    def setUp(self):
        # Reset model data before every test
        models.accounts.clear()
        models.sims.clear()
        models.pack_types.clear()
        models.purchased_packs.clear()

    def test_account_registration(self):
        models.register_account("ACC-01", "Test Account")

        self.assertIn("ACC-01", models.accounts)
        self.assertEqual(
            models.accounts["ACC-01"]["account_name"],
            "Test Account"
        )

    def test_sim_registration(self):
        models.register_account("ACC-01", "Test Account")
        models.register_sim("SIM001", "ACC-01", "IoT")

        self.assertIn("SIM001", models.sims)
        self.assertEqual(
            models.sims["SIM001"]["account_id"],
            "ACC-01"
        )

    def test_pack_type_creation(self):
        models.create_pack_type("PK-S", 1000, 30, 100, 2)

        self.assertIn("PK-S", models.pack_types)
        self.assertEqual(models.pack_types["PK-S"]["data_mb"], 1000)

    def test_pack_purchase(self):
        models.register_account("ACC-01", "Test Account")
        models.create_pack_type("PK-S", 1000, 30, 100, 2)
        models.purchase_pack("PACK001", "ACC-01", "PK-S")

        self.assertIn("PACK001", models.purchased_packs)
        self.assertEqual(
            models.purchased_packs["PACK001"]["account_id"],
            "ACC-01"
        )

    def test_sim_suspension_and_resumption(self):
        models.register_account("ACC-01", "Test Account")
        models.register_sim("SIM001", "ACC-01", "IoT")

        models.suspend_sim("SIM001")
        self.assertEqual(models.sims["SIM001"]["state"], "SUSPENDED")

        models.resume_sim("SIM001")
        self.assertNotEqual(models.sims["SIM001"]["state"], "SUSPENDED")


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PooledDataEngine()

        self.engine.accounts["ACC-01"] = {
            "account_name": "Test Account",
            "city": "Bengaluru",
            "contact_mobile": "9999999999"
        }

        self.engine.pack_types["PK-S"] = {
            "data_mb": 1000,
            "validity_days": 30,
            "price_rs": 100,
            "overage_rate_per_mb": 2
        }

        self.engine.register_sim(
            "SIM001", "ACC-01", "IoT", "2026-10-01"
        )
        self.engine.activate_sim("SIM001", "2026-10-01")

    def test_sim_registration(self):
        self.assertIn("SIM001", self.engine.sims)
        self.assertEqual(
            self.engine.sims["SIM001"]["state"],
            "ACTIVE"
        )

    def test_pack_purchase_and_validity(self):
        self.engine.buy_pack("ACC-01", "PK-S", "2026-10-01")

        pack = self.engine.purchased_packs[0]

        self.assertEqual(pack["expiry_date"], "2026-10-30")
        self.assertEqual(pack["remaining_mb"], 1000)

    def test_shared_data_pool(self):
        self.engine.buy_pack("ACC-01", "PK-S", "2026-10-01")

        self.engine.register_sim(
            "SIM002", "ACC-01", "IoT", "2026-10-01"
        )
        self.engine.activate_sim("SIM002", "2026-10-01")

        self.engine.process_usage_row(
            "2026-10-02", "SIM001", 200, 2
        )
        self.engine.process_usage_row(
            "2026-10-02", "SIM002", 200, 3
        )

        balance = self.engine.get_pool_balance(
            "ACC-01", "2026-10-02"
        )

        self.assertEqual(balance, 600)

    def test_fair_use_and_overage(self):
        self.engine.buy_pack("ACC-01", "PK-S", "2026-10-01")

        result = self.engine.process_usage_row(
            "2026-10-02", "SIM001", 235.2, 2
        )

        self.assertEqual(result[0], 200)
        self.assertAlmostEqual(result[1], 35.2)

        charge = self.engine.calculate_overage_charges()
        self.assertEqual(charge, 72)

    def test_suspension_and_resumption(self):
        self.engine.buy_pack("ACC-01", "PK-S", "2026-10-01")

        self.engine.suspend_sim("SIM001", "2026-10-05")
        self.assertEqual(
            self.engine.sims["SIM001"]["state"],
            "SUSPENDED"
        )

        result = self.engine.process_usage_row(
            "2026-10-06", "SIM001", 50, 2
        )

        self.assertIsNone(result)
        self.assertEqual(
            self.engine.errors[-1]["reason"],
            "SIM_SUSPENDED"
        )

        self.engine.resume_sim("SIM001", "2026-10-07")
        self.assertEqual(
            self.engine.sims["SIM001"]["state"],
            "ACTIVE"
        )

    def test_statement_and_gst(self):
        self.engine.buy_pack("ACC-01", "PK-S", "2026-10-01")

        self.engine.process_usage_row(
            "2026-10-02", "SIM001", 235.2, 2
        )

        self.engine.create_statement(
            "ACC-01", "2026-10-01", "2026-10-30"
        )

        statement = self.engine.statements[0]

        self.assertEqual(statement["pack_cost_rs"], 100)
        self.assertEqual(statement["overage_charge_rs"], 72)
        self.assertEqual(statement["gst_rs"], 31)
        self.assertEqual(statement["total_rs"], 203)


if __name__ == "__main__":
    unittest.main(verbosity=2)
