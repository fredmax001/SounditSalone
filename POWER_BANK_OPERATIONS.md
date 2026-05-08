# SOUND IT SALONE — Power Bank Operations Guide

> **Version:** 1.0  
> **Date:** May 2026  
> **Audience:** Agents, Developers, Vendors, Venue Partners, Internal Team  
> **Classification:** Internal Operations Document

---

## 1. System Overview

SOUND IT SALONE operates a **centralized smart power bank rental network** across Sierra Leone.

Power banks are installed inside:

- Restaurants
- Bars & Nightclubs
- Cafés
- Hotels
- Retail Stores
- Event Venues

### Ownership Model

| Asset | Owner |
|-------|-------|
| Power Banks | **SOUND IT SALONE** |
| Charging Stations | **SOUND IT SALONE** |
| Wallet System | **SOUND IT SALONE** |
| Customer Data | **SOUND IT SALONE** |
| Venue Space | **Hosting Partner** |

**Venues act only as Hosting Partners.** They do not own devices, control pricing, or access customer financial data.

---

## 2. Core System Structure

### 2.1 User App (Mobile / Web)

End users can:

- **Discover** nearby charging stations via map or list view
- **Scan QR codes** on station slots to initiate rental
- **Rent power banks** with real-time availability checks
- **Pay** using wallet balance, Orange Money, or card
- **Return** power banks at any partner venue
- **View rental history**, receipts, and active rentals
- **Add funds** to their wallet
- **Withdraw refunds** to their payment method

### 2.2 Wallet System

The wallet powers the entire platform. A single wallet balance can be used for:

- Power bank rentals
- Event tickets
- Venue payments
- Future platform services

#### Wallet Funding Methods

| Method | Availability | Processing |
|--------|-------------|------------|
| Orange Money | Sierra Leone | Instant |
| Visa Card | International | Instant |
| Mastercard | International | Instant |

---

## 3. Payment Flow

### Option A — Wallet Payment (Recommended)

1. User adds money to wallet via Orange Money or card
2. User scans QR code at station
3. Rental fee is deducted automatically from wallet balance
4. Power bank unlocks immediately

### Option B — Direct Payment

1. User scans QR code at station
2. System detects insufficient wallet balance
3. Orange Money popup **or** card payment screen opens
4. User completes payment
5. System confirms payment and unlocks power bank

---

## 4. Power Bank Rental Flow

### Step 1 — Station Selection

User views station details:

```
┌─────────────────────────────┐
│  Paddy's Nightclub          │
│  12 Lightfoot Boston Street │
│  ⭐ 4.8 · Open Now          │
│                             │
│  Power Banks: 8 / 10        │
│  Available                  │
│                             │
│  [ Scan QR to Rent ]        │
└─────────────────────────────┘
```

### Step 2 — QR Scan

The QR code encodes:

- `station_id` — unique station identifier
- `slot_id` — specific slot in the station
- `device_serial` — serial number of the power bank

### Step 3 — Payment Authorization

System validates:

- **Wallet balance** ≥ rental deposit
- **OR** Orange Money authorization
- **OR** Card payment token

If payment fails, the slot remains locked and no rental is created.

### Step 4 — Power Bank Release

- Station slot unlocks automatically
- Rental timer begins **immediately**
- User receives confirmation with rental ID and return instructions
- Active rental appears in user's dashboard

---

## 5. Rental Pricing System

### Standard Pricing (Regular Users)

| Duration | Fee |
|----------|-----|
| First Hour | Free |
| Each Additional Hour | Le 5 |
| Daily Cap | Le 50 |
| Max Rental Period | 24 Hours |

> **Note:** Pricing is configurable per station and can be adjusted by admin for promotions or peak events.

### Deposit Model

- A refundable deposit is held at rental start
- Deposit covers the maximum possible rental fee (24h cap)
- Unused deposit is refunded automatically upon return
- If power bank is not returned, deposit is forfeited

---

## 6. Return Process

Users can return power banks to:

- **Same venue** where rented
- **Any** SOUND IT SALONE partner venue

This creates a **nationwide charging network** — users rent in Freetown, return in Bo, charge in Makeni.

### Return Logic

When a power bank is inserted into any station slot:

1. Station detects device via RFID / serial scan
2. System calculates:
   - Total rental time
   - Final fee (based on pricing rules)
   - Refund amount (deposit minus fee)
3. Refund is credited to user wallet instantly
4. Rental marked as `returned`
5. Station slot becomes available

---

## 7. User Account Types

### A. Regular Users

- Standard rental pricing applies
- Can rent at any station
- Can return at any station
- Full access to wallet, history, and settings

### B. Venue Partner Accounts

Each venue partner receives:

- **1 Owner Account** — full venue dashboard access
- **2 Staff Accounts** — limited access with free usage benefits

#### Staff Free Usage Rule

| Duration | Status | Charge |
|----------|--------|--------|
| 0–60 minutes | ✅ Free | Le 0 |
| 61+ minutes | ❌ Standard | Le 5/hour |

> **Purpose:** Prevents abuse while rewarding partners. Staff cannot keep devices indefinitely without charges.

---

## 8. Venue Partner Role

### What Venues Do NOT Control

- ❌ Power bank ownership
- ❌ Station hardware
- ❌ Wallet system
- ❌ Customer data
- ❌ Pricing
- ❌ User accounts

### What Venues DO

- ✅ Host charging stations (provide power + physical space)
- ✅ Help promote usage to customers
- ✅ Earn commission on rentals
- ✅ Monitor station status via dashboard
- ✅ Report faulty devices

### Venue Benefits

| Benefit | Description |
|---------|-------------|
| **Increased Dwell Time** | Customers stay longer when phones are charging |
| **Revenue Share** | 5–10% commission on all rentals at their station |
| **Staff Perks** | Owner + 2 staff get 1 hour free per rental |
| **Marketing Value** | Listed on SOUND IT SALONE app as a charging point |
| **Customer Acquisition** | New foot traffic from users searching for stations |

---

## 9. Vendor / Venue Dashboard

Venue partners access a dedicated dashboard showing:

### Station Status

- Available units
- Empty slots
- Faulty / offline units
- Total rentals today

### Earnings

- Daily earnings
- Weekly earnings
- Monthly earnings
- Commission breakdown

### Staff Activity

- Staff rental history
- Overuse charges incurred
- Return compliance

### Reports

- Peak usage hours
- Popular stations
- Revenue trends

---

## 10. SOUND IT SALONE Admin Control

The main admin system has full control over:

| Function | Capability |
|----------|-----------|
| **Pricing** | Set hourly rates, daily caps, deposits per station |
| **Device Inventory** | Add, remove, reassign, track all power banks |
| **Wallet Transactions** | View all deposits, withdrawals, refunds |
| **Fraud Prevention** | Flag suspicious accounts, suspend users, investigate |
| **User Management** | View profiles, rental history, ban / unban |
| **Vendor Management** | Onboard venues, set commission rates, deactivate |
| **Revenue Settlement** | Calculate payouts, generate commission reports |
| **System Settings** | Maintenance mode, global announcements, feature flags |

---

## 11. Device Tracking System

Every power bank has a digital twin in the system:

```
Device Record
├── Serial Number:     PB-SL-001-2026
├── Station ID:        ST-Freetown-003
├── Status:            Available / Rented / Faulty / Missing
├── Battery Health:    87%
├── Total Rentals:     142
├── Total Revenue:     Le 3,210
├── Last Return:       2026-05-06 14:32
├── Assigned User:     —
└── Usage Logs:        [array of rental events]
```

---

## 12. Anti-Theft System

If a power bank is not returned within the maximum rental period (24 hours):

1. **Deposit Forfeited** — full deposit charged to user
2. **Account Flagged** — user marked for review
3. **Device Marked Missing** — removed from available inventory
4. **Account Suspension** — repeat offenders may be suspended
5. **Recovery Process** — admin can initiate recovery or insurance claim

### User Reminders

- Push notification at **22 hours** — "Return soon to avoid charges"
- Push notification at **23 hours** — "1 hour left — return now"
- Final notice at **24 hours** — "Deposit forfeited. Contact support."

---

## 13. Revenue Flow

### Step 1 — User Payment

User pays via:

- Wallet balance
- Orange Money
- Visa / Mastercard

**All funds flow directly to SOUND IT SALONE.**

### Step 2 — Automatic Commission Split

System calculates in real time:

```
User Payment:        Le 100
├─ Venue Commission:  Le 8   (8%)
├─ Maintenance Fund:  Le 5   (5%)
└─ Platform Revenue:  Le 87  (87%)
```

> Commission percentages are configurable per venue contract.

### Step 3 — Settlement

- Venue commissions accumulate in venue wallet
- Venues can request payout to Orange Money or bank account
- Payouts processed weekly or on-demand (configurable)

---

## 14. Future Expansion

The same wallet and station infrastructure will later support:

- **Event Tickets** — purchase and scan at entry
- **Venue Ordering** — table service, food & drinks
- **Cashless Festivals** — wristband-linked wallet payments
- **Rewards Points** — loyalty program for frequent users
- **DJ & Artist Bookings** — direct booking via platform
- **Transport Payments** — future integration with transit
- **Merchant Payments** — small business checkout

---

## 15. Quick Reference — Agent Explanation

> **"SOUND IT SALONE owns all power banks and charging stations. Venues only host the stations and earn a small commission from rentals. Users scan QR codes to rent power banks using wallet balance, Orange Money, or Visa cards. Venue owners and two staff members receive free usage for one hour, after which normal charges apply automatically. Users can return power banks at any partner venue across the network."**

---

## 16. Contact & Support

| Role | Contact | Purpose |
|------|---------|---------|
| Operations | ops@sounditentsl.com | Station issues, logistics |
| Vendor Support | partners@sounditentsl.com | Venue onboarding, payouts |
| Technical | dev@sounditentsl.com | API, integrations, bugs |
| Emergency | +232 79 123 456 | Urgent hardware failure |

---

*Document maintained by SOUND IT SALONE Operations Team. Updates published as system evolves.*
