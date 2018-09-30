DROP TABLE IF EXISTS public.idealista;

CREATE TABLE public.idealista (
  apiKey VARCHAR(40),
  apiSecret VARCHAR(20),
  numUsed INT DEFAULT 0,
  lastDay DATE DEFAULT CURRENT_DATE,
  lastTime TIME DEFAULT CURRENT_TIME
);

INSERT INTO public.idealista (apiKey, apiSecret) VALUES ('ieclz9s4orpj4eny7d0mma1rhznxros2', 'UALB1qhLPSuv');
