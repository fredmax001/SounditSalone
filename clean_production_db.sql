-- Clean Production Database Script
-- Removes all fake/test data while preserving super admin accounts and system configuration
-- Run with: sqlite3 soundit_local.db < clean_production_db.sql

PRAGMA foreign_keys = OFF;

-- ============================================
-- 1. CLEAR ALL ACTIVITY/LOG/OTP DATA
-- ============================================
DELETE FROM admin_activity_logs;
DELETE FROM user_activity_logs;
DELETE FROM search_logs;
DELETE FROM otp_codes;
DELETE FROM notifications;
DELETE FROM monime_webhook_logs;
DELETE FROM monime_payments;
DELETE FROM payment_verifications;
DELETE FROM verification_requests;

-- ============================================
-- 2. CLEAR ALL USER-GENERATED CONTENT
-- ============================================
DELETE FROM contact_submissions;
DELETE FROM support_ticket_replies;
DELETE FROM support_tickets;
DELETE FROM recaps;
DELETE FROM recap_likes;
DELETE FROM reviews;
DELETE FROM deals;
DELETE FROM crews;

-- ============================================
-- 3. CLEAR ALL TRANSACTIONAL DATA
-- ============================================
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM tickets;
DELETE FROM ticket_tiers;
DELETE FROM food_order_items;
DELETE FROM food_orders;
DELETE FROM bookings;
DELETE FROM reservations;
DELETE FROM restaurant_reservations;
DELETE FROM power_bank_rentals;
DELETE FROM power_bank_stations;
DELETE FROM ai_menu_jobs;

-- ============================================
-- 4. CLEAR ALL EVENT DATA
-- ============================================
DELETE FROM featured_events;
DELETE FROM disabled_events;
DELETE FROM event_follows;
DELETE FROM events;

-- ============================================
-- 5. CLEAR ALL SOCIAL/FOLLOW DATA
-- ============================================
DELETE FROM artist_follows;
DELETE FROM event_follows;
DELETE FROM organizer_follows;
DELETE FROM vendor_follows;

-- ============================================
-- 6. CLEAR ALL VENUE/CLUB/RESTAURANT LISTINGS
-- ============================================
DELETE FROM featured_items;
DELETE FROM venue_managers;
DELETE FROM venue_subscriptions;
DELETE FROM venue_profiles;
DELETE FROM venues;
DELETE FROM clubs;
DELETE FROM food_spots;
DELETE FROM restaurant_profiles;
DELETE FROM business_profiles;
DELETE FROM vendor_profiles;

-- ============================================
-- 7. CLEAR SPORTS DATA (DEPRECATED FEATURE)
-- ============================================
DELETE FROM sports_facilities;

-- ============================================
-- 8. CLEAR SUBSCRIPTION DATA LINKED TO USERS
-- ============================================
DELETE FROM organizer_subscriptions;
DELETE FROM user_subscriptions;

-- ============================================
-- 9. CLEAR ORGANIZER PROFILES
-- ============================================
DELETE FROM organizer_profiles;

-- ============================================
-- 10. DELETE ALL USERS EXCEPT SUPER_ADMINS
-- ============================================
DELETE FROM users WHERE role != 'SUPER_ADMIN';

PRAGMA foreign_keys = ON;
