DROP TABLE IF EXISTS public.control;

CREATE TABLE public.control (
    fecha DATE DEFAULT CURRENT_DATE,
    hora TIME DEFAULT CURRENT_TIME
    proveedor VARCHAR(30),
    totalPaginas INT,
    totalInmuebles INT,
    totalInsertados INT,
    totalBaja INT,
    tiempoEjecucion REAL
);

ALTER TABLE control ADD PRIMARY KEY (fecha, proveedor, hora);

CREATE UNIQUE INDEX "control-index"
    ON public.control USING btree
    (fecha ASC NULLS LAST, proveedor ASC NULLS LAST)
    TABLESPACE pg_default;
