// MongoDB initialization script for BanKa MVP
// This script sets up initial database structure and indexes

db = db.getSiblingDB('banka_db');

// Create collections with indexes for optimal performance
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "id": 1 }, { unique: true });
db.users.createIndex({ "wallet_address": 1 });

db.createCollection('events');
db.events.createIndex({ "id": 1 }, { unique: true });
db.events.createIndex({ "organizer_id": 1 });
db.events.createIndex({ "date": 1 });
db.events.createIndex({ "is_active": 1 });

db.createCollection('tokens');
db.tokens.createIndex({ "id": 1 }, { unique: true });
db.tokens.createIndex({ "contract_address": 1 }, { unique: true });
db.tokens.createIndex({ "event_id": 1 });
db.tokens.createIndex({ "is_active": 1 });

db.createCollection('purchases');
db.purchases.createIndex({ "id": 1 }, { unique: true });
db.purchases.createIndex({ "user_id": 1 });
db.purchases.createIndex({ "token_address": 1 });
db.purchases.createIndex({ "timestamp": 1 });

db.createCollection('transfers');
db.transfers.createIndex({ "id": 1 }, { unique: true });
db.transfers.createIndex({ "from_user_id": 1 });
db.transfers.createIndex({ "to_address": 1 });
db.transfers.createIndex({ "timestamp": 1 });

db.createCollection('offline_transfers');
db.offline_transfers.createIndex({ "id": 1 }, { unique: true });
db.offline_transfers.createIndex({ "to_user_id": 1 });
db.offline_transfers.createIndex({ "from_cashier_id": 1 });
db.offline_transfers.createIndex({ "timestamp": 1 });

print('✅ BanKa database initialized successfully with indexes');
