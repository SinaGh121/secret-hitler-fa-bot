# مجموعهٔ نقش‌ها و مسیر تخته برای تعداد متفاوت بازیکنان
ROLE_LIBERAL = "لیبرال"
ROLE_FASCIST = "فاشیست"
ROLE_HITLER = "هیتلر"

PARTY_LIBERAL = "لیبرال"
PARTY_FASCIST = "فاشیست"

POLICY_LIBERAL = "لیبرال"
POLICY_FASCIST = "فاشیست"

ACTION_POLICY = "سیاست"
ACTION_INSPECT = "بازرسی"
ACTION_CHOOSE = "انتخاب"
ACTION_KILL = "اعدام"
ACTION_WIN = "پیروزی"

playerSets = {
    3: {  # فقط برای تست
        "roles": [
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            None,
            None,
            ACTION_POLICY,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    4: {  # فقط برای تست
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            None,
            None,
            ACTION_POLICY,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    5: {
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            None,
            None,
            ACTION_POLICY,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    6: {
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            None,
            None,
            ACTION_POLICY,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    7: {
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            None,
            ACTION_INSPECT,
            ACTION_CHOOSE,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    8: {
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            None,
            ACTION_INSPECT,
            ACTION_CHOOSE,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    9: {
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_FASCIST,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            ACTION_INSPECT,
            ACTION_INSPECT,
            ACTION_CHOOSE,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
    10: {
        "roles": [
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_LIBERAL,
            ROLE_FASCIST,
            ROLE_FASCIST,
            ROLE_FASCIST,
            ROLE_HITLER
        ],
        "track": [
            ACTION_INSPECT,
            ACTION_INSPECT,
            ACTION_CHOOSE,
            ACTION_KILL,
            ACTION_KILL,
            ACTION_WIN
        ]
    },
}

# بستهٔ سیاست‌ها
policies = [
    POLICY_LIBERAL,
    POLICY_LIBERAL,
    POLICY_LIBERAL,
    POLICY_LIBERAL,
    POLICY_LIBERAL,
    POLICY_LIBERAL,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST,
    POLICY_FASCIST
]
