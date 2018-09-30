DROP TABLE IF EXISTS public.idealista_api;

CREATE TABLE public.idealista_api (
  apiKey VARCHAR(40),
  apiSecret VARCHAR(20),
  apiUser VARCHAR(120),
  numUsed INT DEFAULT 0,
  lastDay DATE DEFAULT CURRENT_DATE,
  lastTime TIME DEFAULT CURRENT_TIME
);

INSERT INTO public.idealista_api (apiKey, apiSecret, apiuser) VALUES ('ieclz9s4orpj4eny7d0mma1rhznxros2', 'UALB1qhLPSuv', 'ricardo.martinez.monje@gmail.com');
INSERT INTO public.idealista_api (apiKey, apiSecret, apiuser) VALUES ('f8yerl7lnyiivv1nqt2cl9p52opgu32p', 'pSIS6wlU7Kb3', 'apttoyou@mail.com');
INSERT INTO public.idealista_api (apiKey, apiSecret, apiuser) VALUES ('znk9n0ms62wy4np9ohrylqnrno0clvq9', 'TI9jfWEtzpHJ', 'julbrun@hotmail.com');
