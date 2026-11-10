
# ECE-005: Main Application

# Import functions from models.py

from models import (
    register_account,
    register_sim,
    create_pack_type,
    purchase_pack,
    display_accounts,
    display_sims,
    display_pack_types,
    display_purchased_packs,
    suspend_sim,
    resume_sim,
    display_sim_history,
    process_daily_usage
)


# STEP 1: Register accounts

register_account("ACC001", "Customer One")
register_account("ACC002", "Customer Two")


# STEP 2: Register SIM cards

register_sim("SIM001", "ACC001", "Vehicle Tracker")
register_sim("SIM002", "ACC001", "Smart Meter")
register_sim("SIM003", "ACC002", "GPS Tracker")


# STEP 3: Create data packs

create_pack_type("PACK001", 1000, 30, 99, 0.10)
create_pack_type("PACK002", 5000, 45, 399, 0.05)


# STEP 4: Purchase data packs

purchase_pack("PUR001", "ACC001", "PACK001")
purchase_pack("PUR002", "ACC001", "PACK002")
purchase_pack("PUR003", "ACC002", "PACK001")


# STEP 5: Suspend SIM001

suspend_sim("SIM001")


# STEP 6: Try suspending SIM001 again

suspend_sim("SIM001")


# STEP 7: Resume SIM001

resume_sim("SIM001")


# STEP 8: Try resuming SIM001 again

resume_sim("SIM001")


# STEP 9: Test an invalid SIM

suspend_sim("SIM999")


# STEP 10: Display SIM history

display_sim_history("SIM001")


# STEP 11: Display final information

display_accounts()
display_sims()
display_pack_types()
display_purchased_packs()
print("\n--- DAILY DATA USAGE PROCESSING ---")
process_daily_usage()
