DROP TABLE IF EXISTS public.t9m1732;

CREATE TABLE public.t9m1732 (
    realestate VARCHAR(30),
    dateInserted DATE DEFAULT CURRENT_DATE,
    propertyCode BIGINT,
    externalReference VARCHAR(70),
    address VARCHAR(200),
    neighborhood VARCHAR(70),
    district VARCHAR(50),
    municipality VARCHAR(60),
    province VARCHAR(30),
    country VARCHAR(2),
    latitude REAL,
    longitude REAL,
    distance INTEGER,
    thumbnail VARCHAR(300),
    url VARCHAR(200),
    propertyType VARCHAR(15),
    constructionYear INT,
    lastRefurbished INT,
    status VARCHAR(15),
    rooms INTEGER,
    bathrooms INTEGER,
    terrace VARCHAR(5),
    terraceSize REAL,
    storageRoom VARCHAR(9),
    heating VARCHAR(5),
    hasLift VARCHAR(5),
    newDevelopment VARCHAR(5),
    exterior VARCHAR(11),
    size REAL,
    floor VARCHAR(3),
    price REAL,
    priceByArea REAL,
    sold DATE
);

CREATE UNIQUE INDEX "t9m1732-index"
    ON public.t9m1732 USING btree
    (realestate ASC NULLS LAST, propertyCode ASC NULLS LAST)
    TABLESPACE pg_default;
