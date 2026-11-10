
# Decision Log
## Project: Prepaid IoT SIM Pooled Data Pack Engine

### 1. Programming Language
**Decision:** Python

**Reason:** Python provides simple file handling, data processing and implementation of business rules.

### 2. Data Storage
**Decision:** CSV files

**Reason:** CSV files are lightweight, easy to read and suitable for storing account, SIM, pack, usage and output records.

### 3. Data Pack Management
**Decision:** Oldest valid pack is consumed first.

**Reason:** This ensures predictable pooled data usage and pack expiry management.

### 4. Shared Data Pool
**Decision:** Data is shared among active SIMs belonging to the same account.

**Reason:** It allows multiple SIMs to use a common purchased data balance.

### 5. Fair Usage Policy
**Decision:** Each SIM has a fair-use limit of 20% of the account's purchased data pool per cycle.

**Reason:** This prevents one SIM from consuming an unfair share of the pooled data.

### 6. Overage Calculation
**Decision:** Excess usage is charged per SIM per day, rounded up to the next whole MB.

**Reason:** This ensures consistent and transparent billing.

### 7. SIM Lifecycle
**Decision:** SIMs support registration, activation, suspension, resumption, expiry and deactivation.

**Reason:** These states represent the different stages of SIM operation.

### 8. Grace Period
**Decision:** A seven-day grace period is provided after pack expiry.

**Reason:** It allows customers to renew their data packs without immediate re-registration.

### 9. Billing
**Decision:** An 18% GST is applied to the subtotal.

**Reason:** This provides a consistent final billing calculation.

### 10. Error Handling
**Decision:** Invalid operations and usage records are recorded in errors.csv.

**Reason:** This makes errors traceable and helps validate system behaviour.
