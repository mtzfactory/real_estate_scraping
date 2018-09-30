-- Cuadro de mandos general.
SELECT realestate,
	COUNT(propertycode) AS Inmuebles,
    MAX(dateinserted) AS UltimaAlta,
    COUNT(sold) AS Vendidos,
    MAX(sold) AS UltimaBaja
FROM public.t9m1732 GROUP BY realestate;
