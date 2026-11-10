

# ECE-005: Account, SIM and Data Pack Management

from datetime import date, timedelta
import csv

# Storage
accounts = {}
sims = {}
pack_types = {}
purchased_packs = {}
billing_records = []


# 1. Register an account
def register_account(account_id, account_name):

    if not account_id or not account_name:
        print("Error: Account details cannot be empty.")
        return False

    if account_id in accounts:
        print("Error: Account already exists.")
        return False

    accounts[account_id] = {
        "account_name": account_name,
        "sim_iccids": [],
        "pack_ids": []
    }

    print("Account registered successfully!")
    return True



def register_sim(iccid, account_id, device_type):

    if not iccid or not device_type:
        print("Error: SIM details cannot be empty.")
        return False

    if account_id not in accounts:
        print("Error: Account does not exist.")
        return False

    if iccid in sims:
        print("Error: SIM already registered.")
        return False

    sims[iccid] = {
        "account_id": account_id,
        "device_type": device_type,
        "state": "ACTIVE",
        "activated_on": date.today(),
        "history": [
            {
                "action": "ACTIVATED",
                "date": date.today()
            }
        ]
    }

    accounts[account_id]["sim_iccids"].append(iccid)

    print("SIM registered successfully!")
    return True



# 3. Create a data pack type
def create_pack_type(pack_type_id, data_mb,
                     validity_days, price, overage_rate):

    if not pack_type_id:
        print("Error: Pack ID cannot be empty.")
        return False

    if pack_type_id in pack_types:
        print("Error: Pack type already exists.")
        return False

    if data_mb <= 0 or validity_days <= 0:
        print("Error: Data and validity must be positive.")
        return False

    if price < 0 or overage_rate < 0:
        print("Error: Price and overage rate cannot be negative.")
        return False

    pack_types[pack_type_id] = {
        "data_mb": data_mb,
        "validity_days": validity_days,
        "price": price,
        "overage_rate": overage_rate
    }

    print("Data pack type created successfully!")
    return True


# 4. Purchase a data pack
def purchase_pack(pack_id, account_id, pack_type_id):

    if account_id not in accounts:
        print("Error: Account does not exist.")
        return False

    if pack_type_id not in pack_types:
        print("Error: Data pack type does not exist.")
        return False

    if pack_id in purchased_packs:
        print("Error: Purchase ID already exists.")
        return False

    # Get pack details
    pack = pack_types[pack_type_id]

    # Record purchase date
    purchase_date = date.today()

    # Calculate expiry date
    expiry_date = purchase_date + timedelta(
        days=pack["validity_days"] - 1
    )

    # Store purchased pack
    purchased_packs[pack_id] = {
        "account_id": account_id,
        "pack_type_id": pack_type_id,
        "purchase_date": purchase_date,
        "expiry_date": expiry_date,
        "total_data_mb": pack["data_mb"],
        "remaining_data_mb": pack["data_mb"],
        "price": pack["price"],
        "overage_rate": pack["overage_rate"]
    }

    accounts[account_id]["pack_ids"].append(pack_id)

    print("Data pack purchased successfully!")
    return True


# 5. Display accounts
def display_accounts():

    print("\n--- REGISTERED ACCOUNTS ---")

    for account_id, details in accounts.items():

        print("Account ID:", account_id)
        print("Customer:", details["account_name"])
        print("SIMs:", details["sim_iccids"])
        print("Purchased Packs:", details["pack_ids"])


# 6. Display SIMs
def display_sims():

    print("\n--- REGISTERED SIMS ---")

    for iccid, details in sims.items():

        print("ICCID:", iccid)
        print("Account:", details["account_id"])
        print("Device:", details["device_type"])
        print("State:", details["state"])


# 7. Display available pack types
def display_pack_types():

    print("\n--- AVAILABLE DATA PACKS ---")

    for pack_id, details in pack_types.items():

        print("Pack ID:", pack_id)
        print("Data:", details["data_mb"], "MB")
        print("Validity:", details["validity_days"], "days")
        print("Price: Rs.", details["price"])
        print("Overage Rate:", details["overage_rate"])
        print("--------------------------")


# 8. Display purchased packs
def display_purchased_packs():

    print("\n--- PURCHASED DATA PACKS ---")

    for pack_id, details in purchased_packs.items():

        print("Purchase ID:", pack_id)
        print("Account:", details["account_id"])
        print("Pack Type:", details["pack_type_id"])
        print("Purchase Date:", details["purchase_date"])
        print("Expiry Date:", details["expiry_date"])
        print("Total Data:", details["total_data_mb"], "MB")
        print("Remaining Data:",
              details["remaining_data_mb"], "MB")
        print("Price: Rs.", details["price"])
        print("--------------------------")

# 9. Suspend a SIM
def suspend_sim(iccid, action_date=None):

    if iccid not in sims:
        print("Error: SIM does not exist.")
        return False

    if sims[iccid]["state"] == "SUSPENDED":
        print("Error: SIM is already suspended.")
        return False

    if sims[iccid]["state"] == "EXPIRED":
        print("Error: Expired SIM cannot be suspended.")
        return False

    if sims[iccid]["state"] == "DEACTIVATED":
        print("Error: SIM is deactivated.")
        return False

    if action_date is None:
        action_date = date.today()

    sims[iccid]["state"] = "SUSPENDED"

    sims[iccid]["history"].append({
        "action": "SUSPENDED",
        "date": action_date
    })

    print("SIM suspended successfully!")
    return True


# 10. Resume a SIM
def resume_sim(iccid, action_date=None):

    if iccid not in sims:
        print("Error: SIM does not exist.")
        return False

    if sims[iccid]["state"] != "SUSPENDED":
        print("Error: SIM is not suspended.")
        return False

    if action_date is None:
        action_date = date.today()

    sims[iccid]["state"] = "ACTIVE"

    sims[iccid]["history"].append({
        "action": "RESUMED",
        "date": action_date
    })

    print("SIM resumed successfully!")
    return True


# 11. Display SIM history
def display_sim_history(iccid):

    if iccid not in sims:
        print("Error: SIM does not exist.")
        return

    print("\n--- SIM STATUS HISTORY ---")
    print("ICCID:", iccid)

    for event in sims[iccid]["history"]:
        print("Action:", event["action"])
        print("Date:", event["date"])
       

usage_records = []
def process_daily_usage(filename="usage.csv"):
    account_usage = {}

    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                iccid = row["iccid"]
                usage_mb = int(row["usage_mb"])
                usage_date = date.fromisoformat(row["date"])

                # Check whether SIM exists
                if iccid not in sims:
                    print(f"Error: SIM {iccid} does not exist.")
                    continue

                # Check whether SIM is active
                if sims[iccid]["state"] != "ACTIVE":
                    print(f"Error: SIM {iccid} is not active.")
                    continue

                # Check whether usage is valid
                if usage_mb < 0:
                    print("Error: Usage cannot be negative.")
                    continue

                account_id = sims[iccid]["account_id"]

                # Deduct usage from shared data pool
                if not deduct_shared_data(account_id, usage_mb):
                    continue

                # Store usage details
                usage_records.append({
                    "date": usage_date,
                    "iccid": iccid,
                    "usage_mb": usage_mb
                })

                # Calculate account-wise usage
                account_usage[account_id] = (
                    account_usage.get(account_id, 0) + usage_mb
                )

                print(f"Usage recorded: {iccid} - {usage_mb} MB")

        print("\n--- TOTAL ACCOUNT DATA USAGE ---")

        for account_id, total in account_usage.items():
            print(f"Account: {account_id}")
            print(f"Total Usage: {total} MB")

    except FileNotFoundError:
        print("Error: usage.csv file not found.")

    except (ValueError, KeyError):
        print("Error: Invalid data found in usage.csv.")

def deduct_shared_data(account_id, usage_mb):

    if account_id not in accounts:
        print("Error: Account does not exist.")
        return False

    pack_ids = accounts[account_id]["pack_ids"]

    for pack_id in pack_ids:

        pack = purchased_packs[pack_id]

        if date.today() > pack["expiry_date"]:
            continue

        if pack["remaining_data_mb"] >= usage_mb:

            pack["remaining_data_mb"] -= usage_mb

            print(f"Data deducted: {usage_mb} MB")
            print(f"Remaining shared data: {pack['remaining_data_mb']} MB")

            return True

    print("Error: Insufficient shared data available.")
    return False
        