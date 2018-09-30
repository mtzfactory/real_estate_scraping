DROP TABLE IF EXISTS public.users;

CREATE TABLE public.users (
  id INT PRIMARY KEY,
  username VARCHAR(32),
  password_hash VARCHAR(64),
  email VARCHAR(256),
  code VARCHAR(64),
  active BOOLEAN DEFAULT True,
  lastlogin TIMESTAMP
);
