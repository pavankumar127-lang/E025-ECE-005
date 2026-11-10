
from datetime import datetime, timedelta
import csv
import math


class PooledDataEngine:
    def __init__(self):
        self.accounts = {}
        self.sims = {}
        self.pack_types = {}
        self.purchased_packs = []
        self.usage_records = []
        self.pool_logs = []
        self.errors = []
        self.statements = []
        self.fair_use = {}
        self.daily_overage = {}
        self.daily_overage_rates = {}
        self.pending_usage = []

    def add_error(self, source, line_no, reason):
        self.errors.append({
            "source": source,
            "line_no": line_no,
            "reason": reason
        })
    
    def load_accounts(self, filename):
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                account_id = row["account_id"]

                self.accounts[account_id] = {
                    "account_name": row["account_name"],
                    "city": row["city"],
                    "contact_mobile": row["contact_mobile"]
                }

        print("Accounts loaded successfully!")

    def load_sims(self, filename):
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                iccid = row["iccid"]

                self.sims[iccid] = {
                    "account_id": row["account_id"],
                    "device_type": row["device_type"],
                    "registered_date": row["registered_date"],
       
             "state": "REGISTERED",
                    "state_since": row["registered_date"],
                    "suspended": False,
                    "expired_on": None
                }

        print("SIMs loaded successfully!")
    def register_sim(self, iccid, account_id, device_type, registered_date):

     if account_id not in self.accounts:
        self.add_error("commands.txt", 0, "ACCOUNT_NOT_FOUND")
        print("Error: Account does not exist.")
        return

     if iccid in self.sims:
        sim = self.sims[iccid]

        if sim["account_id"] != account_id:
            self.add_error("commands.txt", 0, "SIM_ALREADY_EXISTS")
            print("Error: SIM already exists.")
            return

        can_reregister = sim["state"] == "DEACTIVATED"

        if sim["state"] == "EXPIRED" and sim.get("expired_on"):
            expired_date = datetime.strptime(
                sim["expired_on"], "%Y-%m-%d"
            ).date()

            new_date = datetime.strptime(
                registered_date, "%Y-%m-%d"
            ).date()

            days_after_expiry = (new_date - expired_date).days

            if days_after_expiry > 7:
                can_reregister = True

        if not can_reregister:
            self.add_error("commands.txt", 0, "SIM_ALREADY_EXISTS")
            print("Error: SIM cannot be re-registered yet.")
            return

        sim["device_type"] = device_type
        sim["registered_date"] = registered_date
        sim["state"] = "REGISTERED"
        sim["state_since"] = registered_date
        sim["suspended"] = False
        sim["expired_on"] = None

        print("SIM re-registered successfully!")
        return

     self.sims[iccid] = {
        "account_id": account_id,
        "device_type": device_type,
        "registered_date": registered_date,
        "state": "REGISTERED",
        "state_since": registered_date,
        "suspended": False,
        "expired_on": None
    }

    print("SIM registered successfully!")
    def load_pack_types(self, filename):
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                pack_type = row["pack_type"]

                self.pack_types[pack_type] = {
                    "data_mb": float(row["data_mb"]),
                    "validity_days": int(row["validity_days"]),
                    "price_rs": float(row["price_rs"]),
                    "overage_rate_per_mb": float(
                        row["overage_rate_per_mb"]
                    )
                }

        print("Pack types loaded successfully!")
        
    def buy_pack(self, account_id, pack_type, purchase_date,line_no=None):
        if account_id not in self.accounts:
            print("Error: Account does not exist.")
            return

        if pack_type not in self.pack_types:
            self.add_error(
                "commands.txt",
                line_no if line_no is not None else 0,
                "INVALID_PACK_TYPE"
            )
            print("Error: Pack type does not exist.")
            return

        purchase_day = datetime.strptime(
            purchase_date, "%Y-%m-%d"
        ).date()

        pack_details = self.pack_types[pack_type]

        expiry_date = purchase_day + timedelta(
            days=pack_details["validity_days"] - 1
        )

        self.purchased_packs.append({
            "account_id": account_id,
            "pack_type": pack_type,
            "purchase_date": purchase_date,
            "expiry_date": expiry_date.isoformat(),
            "data_mb": pack_details["data_mb"],
            "remaining_mb": pack_details["data_mb"],
            "price_rs": pack_details["price_rs"],
            "overage_rate_per_mb": pack_details[
                "overage_rate_per_mb"
            ]
        })
        
        # Reactivate SIMs only within 7 days after pack expiry
        for sim in self.sims.values():
            if sim["account_id"] == account_id:
                if sim["state"] == "EXPIRED":
                    expired_on = sim.get("expired_on")

                    if expired_on:
                        expiry_day = datetime.strptime(
                            expired_on, "%Y-%m-%d"
                        ).date()

                        days_after_expiry = (
                            purchase_day - expiry_day
                        ).days

                        if 1 <= days_after_expiry <= 7:
                            sim["state"] = "ACTIVE"
                            sim["state_since"] = purchase_date
                            sim["expired_on"] = None


         
        print("Data pack purchased successfully!")
        
    def activate_sim(self, iccid, activation_date):
        if iccid not in self.sims:
            print("Error: SIM does not exist.")
            return

        sim = self.sims[iccid]

        if sim["state"] == "ACTIVE":
            print("Error: SIM is already active.")
            return

        if sim["state"] in ["EXPIRED", "DEACTIVATED"]:
            print("Error: SIM cannot be activated.")
            return

        sim["state"] = "ACTIVE"
        sim["state_since"] = activation_date

        print("SIM activated successfully!")

    
   
    def suspend_sim(self, iccid, suspend_date, line_no=None):
        if iccid not in self.sims:
            print("Error: SIM does not exist.")
            return

        sim = self.sims[iccid]

        if sim["state"] != "ACTIVE":
            self.add_error(
                "commands.txt",
                line_no if line_no is not None else 0,
                "INVALID_STATE_TRANSITION"
            )
            print("Error: SIM is not active.")
            return

        sim["state"] = "SUSPENDED"
        sim["state_since"] = suspend_date

        print("SIM suspended successfully!")

    def resume_sim(self, iccid, resume_date):
        if iccid not in self.sims:
            print("Error: SIM does not exist.")
            return

        sim = self.sims[iccid]

        if sim["state"] != "SUSPENDED":
            print("Error: SIM is not suspended.")
            return

        sim["state"] = "ACTIVE"
        sim["state_since"] = resume_date

        print("SIM resumed successfully!")
        
    def get_valid_packs(self, account_id, usage_date):
        valid_packs = []

        for pack in self.purchased_packs:
            if pack["account_id"] == account_id:
                if (pack["purchase_date"] <= usage_date
                        <= pack["expiry_date"]):
                    valid_packs.append(pack)

        # Oldest purchased pack must be used first
        valid_packs.sort(key=lambda pack: pack["purchase_date"])

        return valid_packs

    def get_pool_balance(self, account_id, usage_date):
        valid_packs = self.get_valid_packs(
            account_id, usage_date
        )

        total_balance = sum(
            pack["remaining_mb"] for pack in valid_packs
        )

        return total_balance

    def get_fair_use_limit(self, account_id, usage_date):
        valid_packs = self.get_valid_packs(
            account_id, usage_date
        )

        purchased_pool = sum(
            pack["data_mb"] for pack in valid_packs
        )

        return purchased_pool * 0.20
    
    def deduct_pool_data(self, account_id, usage_date, mb_used):
        valid_packs = self.get_valid_packs(
            account_id, usage_date
        )

        remaining_usage = mb_used
        pool_used = 0

        for pack in valid_packs:
            if remaining_usage <= 0:
                break

            available = pack["remaining_mb"]

            deducted = min(available, remaining_usage)

            pack["remaining_mb"] -= deducted
            remaining_usage -= deducted
            pool_used += deducted

        return pool_used, remaining_usage
    
    def calculate_fair_use(self, iccid, account_id, usage_date):
        packs = self.get_valid_packs(
            account_id, usage_date
        )

        purchased_pool = sum(
            pack["data_mb"] for pack in packs
        )

        fair_use_limit = purchased_pool * 0.20

        # Identify the oldest currently valid pack
        if not packs:
            return 0

        oldest_purchase = packs[0]["purchase_date"]

        cycle_key = (iccid, oldest_purchase)

        if cycle_key not in self.fair_use:
            self.fair_use[cycle_key] = 0

        remaining_fair_use = max(
            0,
            fair_use_limit - self.fair_use[cycle_key]
        )

        return remaining_fair_use
    
    def process_usage_row(self, usage_date, iccid, mb_used,
                          line_no, source="usage.csv"):

        if iccid not in self.sims:
            self.add_error(source, line_no, "SIM_DOES_NOT_EXIST")
            return

        sim = self.sims[iccid]
        account_id = sim["account_id"]

        if sim["state"] == "SUSPENDED":
            self.add_error(source, line_no, "SIM_SUSPENDED")
            return

        if sim["state"] != "ACTIVE":
            self.add_error(source, line_no, "NOT_ACTIVE")
            return

        valid_packs = self.get_valid_packs(
            account_id, usage_date
        )

        if not valid_packs:
            self.add_error(source, line_no, "NO_VALID_PACK")
            return

        if mb_used <= 0:
            self.add_error(source, line_no, "INVALID_USAGE")
            return

        # Find the fair-use cycle
        oldest_purchase = valid_packs[0]["purchase_date"]
        cycle_key = (iccid, oldest_purchase)

        if cycle_key not in self.fair_use:
            self.fair_use[cycle_key] = 0

        # Calculate remaining fair-use allowance
        remaining_fair_use = self.calculate_fair_use(
            iccid, account_id, usage_date
        )

        # Only the eligible portion can use pooled data
        eligible_usage = min(mb_used, remaining_fair_use)

        # Deduct eligible usage from the shared pool
        pool_used, pool_shortfall = self.deduct_pool_data(
            account_id, usage_date, eligible_usage
        )

        # Usage beyond fair use or available pool is overage
        overage_mb = (
            mb_used - pool_used
        )

        # Count the entire accepted usage in the fair-use cycle
        self.fair_use[cycle_key] += mb_used
        # Collect overage by SIM and date
        overage_key = (usage_date, iccid)

        if overage_key not in self.daily_overage:
            self.daily_overage[overage_key] = 0

        self.daily_overage[overage_key] += overage_mb

        # Store the applicable overage rate
        self.daily_overage_rates[overage_key] = (
            valid_packs[0]["overage_rate_per_mb"]
        )
        self.usage_records.append({
            "date": usage_date,
            "iccid": iccid,
            "account_id": account_id,
            "mb_used": mb_used,
            "pool_used": pool_used,
            "overage_mb": overage_mb,
            "pool_shortfall": pool_shortfall
        })

        return pool_used, overage_mb
    
    def calculate_overage_charges(self):
        total_overage_charge = 0

        for key, overage_mb in self.daily_overage.items():
            rounded_mb = math.ceil(overage_mb)

            rate = self.daily_overage_rates[key]

            charge = rounded_mb * rate

            total_overage_charge += charge

        return round(total_overage_charge, 2)
    
    def load_usage(self, filename):
        seen = set()

        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)

            for line_no, row in enumerate(reader, start=2):
                try:
                    usage_date = row["date"]
                    datetime.strptime(usage_date, "%Y-%m-%d")

                    iccid = row["iccid"]
                    mb_used = float(row["mb_used"])

                    duplicate_key = (
                        usage_date, iccid
                    )

                    if duplicate_key in seen:
                        self.add_error(
                            filename,
                            line_no,
                            "DUPLICATE_USAGE"
                        )
                        continue

                    seen.add(duplicate_key)

                    self.pending_usage.append({
                        "date": usage_date,
                        "iccid": iccid,
                        "mb_used": mb_used,
                        "line_no": line_no,
                        "source": filename
                    })

                except (ValueError, KeyError):
                    self.add_error(
                        filename,
                        line_no,
                        "INVALID_USAGE_ROW"
                    )

        print("Usage data loaded successfully!")

    
    
        
    def get_sim_states(self):
        results = []

        for iccid, sim in self.sims.items():
            results.append({
                "iccid": iccid,
                "account_id": sim["account_id"],
                "final_state": sim["state"],
                "state_since": sim["state_since"]
            })

        return results
    
    def export_sim_states(self, filename="sim_states.csv"):
        fields = [
            "iccid",
            "account_id",
            "final_state",
            "state_since"
        ]

        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(self.get_sim_states())

        print("SIM states exported successfully!")
        
    def export_errors(self, filename="errors.csv"):
        fields = [
            "source",
            "line_no",
            "reason"
        ]

        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(self.errors)

        print("Errors exported successfully!")
        
    def export_pool_log(self, filename="pool_log.csv"):
        fields = [
            "date",
            "account_id",
            "pool_mb_start",
            "accepted_mb",
            "pool_mb_used",
            "overage_mb",
            "pool_mb_end",
            "active_sims",
            "account_state"
        ]

        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(self.pool_logs)

        print("Pool log exported successfully!")
        
    def export_statements(self, filename="statements.csv"):
        fields = [
            "account_id",
            "period_start",
            "period_end",
            "packs_bought",
            "pack_cost_rs",
            "pool_mb_used",
            "overage_mb",
            "overage_charge_rs",
            "subtotal_rs",
            "gst_rs",
            "total_rs"
        ]

        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(self.statements)

        print("Statements exported successfully!")
        
    def process_pending_usage_for_date(self, process_date):
        remaining_rows = []

        for row in self.pending_usage:
            if row["date"] == process_date:
                self.process_usage_row(
                    row["date"],
                    row["iccid"],
                    row["mb_used"],
                    row["line_no"],
                    row["source"]
                )
            else:
                remaining_rows.append(row)

        self.pending_usage = remaining_rows

        print(
            f"Usage processed for {process_date}"
        )
        
    
    def update_sim_states_for_date(self, process_date):
     for iccid, sim in self.sims.items():
        account_id = sim["account_id"]

        if sim["state"] in ["REGISTERED", "DEACTIVATED", "SUSPENDED"]:
            continue

        valid_packs = self.get_valid_packs(
            account_id, process_date
        )

        # ACTIVE SIMs expire only when no valid pack exists
        if sim["state"] == "ACTIVE":
            if valid_packs:
                continue

            expired_packs = [
                pack for pack in self.purchased_packs
                if pack["account_id"] == account_id
                and pack["expiry_date"] < process_date
            ]

            if not expired_packs:
                continue

            latest_expiry = max(
                pack["expiry_date"] for pack in expired_packs
            )

            sim["state"] = "EXPIRED"
            sim["state_since"] = process_date
            sim["expired_on"] = latest_expiry

        # EXPIRED SIMs must be deactivated after 7 days,
        # even if the account purchases a new pack
        elif sim["state"] == "EXPIRED":
            expired_on = sim.get("expired_on")

            if not expired_on:
                continue

            days_after_expiry = (
                datetime.strptime(
                    process_date, "%Y-%m-%d"
                ).date()
                - datetime.strptime(
                    expired_on, "%Y-%m-%d"
                ).date()
            ).days

            if days_after_expiry > 7:
                sim["state"] = "DEACTIVATED"
                sim["state_since"] = process_date

    def process_day(self, process_date):
        # Record pool balance before usage
        pool_start = {}

        for account_id in self.accounts:
            pool_start[account_id] = self.get_pool_balance(
                account_id, process_date
            )

        # Update SIM states
        self.update_sim_states_for_date(process_date)

        # Process usage for this date
        self.process_pending_usage_for_date(process_date)

        # Generate daily pool logs
        for account_id in self.accounts:
            daily_records = [
                row for row in self.usage_records
                if row["date"] == process_date
                and row["account_id"] == account_id
            ]

            accepted_mb = sum(row["mb_used"] for row in daily_records)
            pool_mb_used = sum(row["pool_used"] for row in daily_records)
            overage_mb = sum(row["overage_mb"] for row in daily_records)

            pool_end = self.get_pool_balance(account_id, process_date)

            active_sims = sum(
                1 for sim in self.sims.values()
                if sim["account_id"] == account_id
                and sim["state"] == "ACTIVE"
            )

            valid_packs = self.get_valid_packs(account_id, process_date)

            account_sims = [
                sim for sim in self.sims.values()
                if sim["account_id"] == account_id
            ]

            if valid_packs:
                account_state = "ACTIVE"
            elif account_sims and all(
                sim["state"] == "DEACTIVATED" for sim in account_sims
            ):
                account_state = "DEACTIVATED"
            else:
                account_state = "EXPIRED"

            self.pool_logs.append({
                "date": process_date,
                "account_id": account_id,
                "pool_mb_start": round(pool_start[account_id], 2),
                "accepted_mb": round(accepted_mb, 2),
                "pool_mb_used": round(pool_mb_used, 2),
                "overage_mb": round(overage_mb, 2),
                "pool_mb_end": round(pool_end, 2),
                "active_sims": active_sims,
                "account_state": account_state
            })
    
    def create_statement(self, account_id, period_start, period_end):
        if account_id not in self.accounts:
            self.add_error(
                "commands.txt", 0,
                f"Account {account_id} does not exist."
            )
            return

        packs = [
            pack for pack in self.purchased_packs
            if pack["account_id"] == account_id
            and period_start <= pack["purchase_date"] <= period_end
        ]

        records = [
            row for row in self.usage_records
            if row["account_id"] == account_id
            and period_start <= row["date"] <= period_end
        ]

        packs_bought = len(packs)
        pack_cost = sum(pack["price_rs"] for pack in packs)

        pool_mb_used = sum(row["pool_used"] for row in records)
        overage_mb = sum(row["overage_mb"] for row in records)

        overage_charge = 0

        for key, amount in self.daily_overage.items():
            usage_date, iccid = key

            if period_start <= usage_date <= period_end:
                if self.sims[iccid]["account_id"] == account_id:
                    rounded_mb = math.ceil(amount)
                    rate = self.daily_overage_rates[key]
                    overage_charge += rounded_mb * rate

        subtotal = pack_cost + overage_charge
        gst = round(subtotal * 0.18)
        total = round(subtotal + gst)

        self.statements.append({
            "account_id": account_id,
            "period_start": period_start,
            "period_end": period_end,
            "packs_bought": packs_bought,
            "pack_cost_rs": round(pack_cost, 2),
            "pool_mb_used": round(pool_mb_used, 2),
            "overage_mb": round(overage_mb, 2),
            "overage_charge_rs": round(overage_charge, 2),
            "subtotal_rs": round(subtotal, 2),
            "gst_rs": gst,
            "total_rs": total
        })

        print(f"Statement generated for {account_id}!")
