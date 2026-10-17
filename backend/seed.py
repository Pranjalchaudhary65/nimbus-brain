TEAMS = [
    {"id": "t1", "name": "Platform"}, {"id": "t2", "name": "Payments"},
    {"id": "t3", "name": "Growth"},   {"id": "t4", "name": "Data"},
]

PEOPLE = [
    {"id": "p01", "name": "Aarav Mehta",    "role": "Engineering Manager", "team": "t1"},
    {"id": "p02", "name": "Priya Nair",     "role": "Senior Engineer",     "team": "t1"},
    {"id": "p03", "name": "Rohan Gupta",    "role": "Engineer",            "team": "t1"},
    {"id": "p04", "name": "Sneha Iyer",     "role": "SRE",                 "team": "t1"},
    {"id": "p05", "name": "Karan Malhotra", "role": "Engineering Manager", "team": "t2"},
    {"id": "p06", "name": "Ananya Rao",     "role": "Senior Engineer",     "team": "t2"},
    {"id": "p07", "name": "Vikram Singh",   "role": "Engineer",            "team": "t2"},
    {"id": "p08", "name": "Neha Kapoor",    "role": "Product Manager",     "team": "t2"},
    {"id": "p09", "name": "Arjun Das",      "role": "Product Manager",     "team": "t3"},
    {"id": "p10", "name": "Isha Verma",     "role": "Frontend Engineer",   "team": "t3"},
    {"id": "p11", "name": "Rahul Jain",     "role": "Mobile Engineer",     "team": "t3"},
    {"id": "p12", "name": "Meera Shah",     "role": "Designer",            "team": "t3"},
    {"id": "p13", "name": "Dev Patel",      "role": "Data Lead",           "team": "t4"},
    {"id": "p14", "name": "Tanvi Joshi",    "role": "Data Engineer",       "team": "t4"},
    {"id": "p15", "name": "Sameer Khan",    "role": "ML Engineer",         "team": "t4"},
    {"id": "p16", "name": "Kavya Reddy",    "role": "Analyst",             "team": "t4"},
]

PROJECTS = [
    {"id": "j1", "name": "auth-service",         "owner": "p02"},
    {"id": "j2", "name": "billing-service",      "owner": "p06"},
    {"id": "j3", "name": "checkout-api",         "owner": "p07"},
    {"id": "j4", "name": "notification-service", "owner": "p03"},
    {"id": "j5", "name": "analytics-pipeline",   "owner": "p14"},
    {"id": "j6", "name": "search-service",       "owner": "p15"},
    {"id": "j7", "name": "web-app",              "owner": "p10"},
    {"id": "j8", "name": "mobile-app",           "owner": "p11"},
]

# (project, depends on project)
DEPENDS_ON = [("j3","j2"), ("j3","j1"), ("j2","j1"), ("j4","j1"), ("j7","j3"),
              ("j7","j1"), ("j7","j6"), ("j8","j3"), ("j8","j4"), ("j6","j5"), ("j5","j2")]

TOPICS = [
    {"id": "tp1", "name": "payments"},  {"id": "tp2", "name": "authentication"},
    {"id": "tp3", "name": "vendor-selection"}, {"id": "tp4", "name": "database"},
    {"id": "tp5", "name": "security"},  {"id": "tp6", "name": "scaling"},
]

DOCS = [
    {"id": "d01", "title": "Payment vendor comparison: Stripe vs Adyen", "author": "p08", "date": "2025-01-20",
     "topics": ["tp1","tp3"], "projects": ["j2"],
     "text": "Compared Stripe and Adyen on fees, developer experience and EU support. Stripe wins on speed of integration; Adyen has better EU coverage."},
    {"id": "d02", "title": "Stripe integration spike results", "author": "p06", "date": "2025-02-03",
     "topics": ["tp1"], "projects": ["j2"],
     "text": "Spike showed Stripe integrates in 3 days with test-mode webhooks. Team recommends Stripe for launch."},
    {"id": "d03", "title": "EU chargeback spike, Q3 2025", "author": "p05", "date": "2025-09-12",
     "topics": ["tp1","tp5"], "projects": ["j2"],
     "text": "EU chargebacks rose 40% and Stripe's EU payment methods are limited. Finance asks for a local acquirer."},
    {"id": "d04", "title": "Adyen EU pilot report", "author": "p07", "date": "2025-10-30",
     "topics": ["tp1","tp3"], "projects": ["j2","j3"],
     "text": "Adyen pilot cut EU declines by 18%. Recommend Adyen for EU and Stripe for the rest of the world."},
    {"id": "d05", "title": "Auth vendor evaluation: Auth0", "author": "p02", "date": "2025-03-05",
     "topics": ["tp2","tp3"], "projects": ["j1"],
     "text": "Auth0 is quick to ship but per-user pricing grows fast with active users."},
    {"id": "d06", "title": "Auth0 cost projection 2026", "author": "p01", "date": "2025-11-14",
     "topics": ["tp2"], "projects": ["j1"],
     "text": "Projected Auth0 bill will triple by mid 2026. Building auth in-house on our identity library is cheaper."},
    {"id": "d07", "title": "Security review of in-house auth", "author": "p04", "date": "2025-12-02",
     "topics": ["tp2","tp5"], "projects": ["j1"],
     "text": "In-house auth passed review with two fixes: rate limiting and refresh token rotation."},
    {"id": "d08", "title": "Analytics storage options", "author": "p14", "date": "2025-04-10",
     "topics": ["tp4"], "projects": ["j5"],
     "text": "ClickHouse and Postgres compared for event analytics. Postgres is fine under 50M events per day."},
    {"id": "d09", "title": "Analytics scale report", "author": "p13", "date": "2026-01-22",
     "topics": ["tp4","tp6"], "projects": ["j5"],
     "text": "Event volume reached 180M a day. Postgres queries time out; ClickHouse is needed."},
    {"id": "d10", "title": "Search relevance experiments", "author": "p15", "date": "2025-06-18",
     "topics": ["tp6"], "projects": ["j6"],
     "text": "Hybrid keyword and vector search improved click-through by 12%."},
]

DECISIONS = [
    {"id": "dc1", "title": "Use Stripe as payment provider", "date": "2025-02-10", "by": "p05",
     "project": "j2", "based_on": ["d01","d02"], "supersedes": None, "status": "superseded"},
    {"id": "dc2", "title": "Use Adyen for EU payments, Stripe elsewhere", "date": "2025-11-05", "by": "p05",
     "project": "j2", "based_on": ["d03","d04"], "supersedes": "dc1", "status": "active"},
    {"id": "dc3", "title": "Adopt Auth0 for authentication", "date": "2025-03-12", "by": "p01",
     "project": "j1", "based_on": ["d05"], "supersedes": None, "status": "superseded"},
    {"id": "dc4", "title": "Build in-house authentication", "date": "2025-12-10", "by": "p01",
     "project": "j1", "based_on": ["d06","d07"], "supersedes": "dc3", "status": "active"},
    {"id": "dc5", "title": "Use Postgres for analytics events", "date": "2025-04-15", "by": "p13",
     "project": "j5", "based_on": ["d08"], "supersedes": None, "status": "superseded"},
    {"id": "dc6", "title": "Migrate analytics events to ClickHouse", "date": "2026-02-01", "by": "p13",
     "project": "j5", "based_on": ["d09"], "supersedes": "dc5", "status": "active"},
]