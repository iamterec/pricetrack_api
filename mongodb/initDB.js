const conn = new Mongo();

// Authentication
const adminDB = conn.getDB("admin");
adminDB.auth(username, password);

// Get main database
let db = adminDB.getSiblingDB("pricetrack");

// Create users collection and validation for it
db.createCollection("users", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["email", "password"],
            properties: {
                email: {
                    bsonType: "string",
                    description: "User's emal."
                },
                password: {
                    bsonType: "binData",
                    description: "User's password."
                },
                avatar: {
                    bsonType: "string",
                    description: "URI of user's avatar picture."
                },
                username: {
                    bsonType: "string",
                    description: "Nickname of username"
                }
            }
        }
    }
});

// Create unique index for "users" collection by email field
db.users.createIndex({ email: 1 }, { unique: true });

// Give permissions for celery backend database
try {
    db = adminDB.getSiblingDB("celery");
    db.createUser({
        user: username,
        pwd: password,
        roles: [{role: "readWrite", db: "celery"}],
        mechanisms: ["SCRAM-SHA-1" ]
    })
} catch(error) {
    print(error)
}
