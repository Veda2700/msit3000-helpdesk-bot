CREATE TABLE faq (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  category TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_query TEXT,
  ai_response TEXT,
  confidence TEXT,
  reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO faq (question, answer, category) VALUES
('How do I reset my password?','Visit portal.techstart.com/reset','Access'),
('How do I connect to VPN?','Download Cisco AnyConnect, use vpn.techstart.com','Network'),
('What is the guest Wi-Fi password?','Guest123! rotated monthly','Network'),
('Who handles hardware issues?','Email it-support@techstart.com','Hardware'),
('How do I access shared drives?','Map drive to \\fileserver\\shared','Access');