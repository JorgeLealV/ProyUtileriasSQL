-- ==========================================================
-- CRUD PROCEDURES Y FUNCTIONS
-- ==========================================================

-- ----------------------------------------------------------
-- 1. CRUD: Usuarios
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_usuario(p_usuario VARCHAR, p_pass VARCHAR, p_nombre VARCHAR, p_credencial VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO Usuarios (Usuario, Password, NombreUsuario, NoCredencial)
    VALUES (p_usuario, p_pass, p_nombre, p_credencial);
END; $$;

CREATE OR REPLACE PROCEDURE sp_actualizar_usuario(p_id INTEGER, p_usuario VARCHAR, p_pass VARCHAR, p_nombre VARCHAR, p_credencial VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE Usuarios SET Usuario = p_usuario, Password = p_pass, NombreUsuario = p_nombre, NoCredencial = p_credencial
    WHERE id_usuario = p_id;
END; $$;

CREATE OR REPLACE PROCEDURE sp_eliminar_usuario(p_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM Usuarios WHERE id_usuario = p_id;
END; $$;

-- ----------------------------------------------------------
-- 2. CRUD: TipoEstaSAT
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tipoestasat(p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipoEstaSAT (DescTEstSAT, id_usuario) VALUES (p_desc, p_id_usu);
END; $$;

CREATE OR REPLACE PROCEDURE sp_actualizar_tipoestasat(p_id INTEGER, p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE TipoEstaSAT SET DescTEstSAT = p_desc, id_usuario = p_id_usu WHERE id_Est = p_id;
END; $$;

-- ----------------------------------------------------------
-- 3. CRUD: TipoNomina
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tiponomina(p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipoNomina (DescTNomina, id_usuario) VALUES (p_desc, p_id_usu);
END; $$;

CREATE OR REPLACE PROCEDURE sp_actualizar_tiponomina(p_id INTEGER, p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE TipoNomina SET DescTNomina = p_desc, id_usuario = p_id_usu WHERE id_tiponom = p_id;
END; $$;

-- ----------------------------------------------------------
-- 4. CRUD: TipoDivision
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tipodivision(p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipoDivision (DescDivision, id_usuario) VALUES (p_desc, p_id_usu);
END; $$;

CREATE OR REPLACE PROCEDURE sp_actualizar_tipodivision(p_id INTEGER, p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE TipoDivision SET DescDivision = p_desc, id_usuario = p_id_usu WHERE id_Division = p_id;
END; $$;

-- ----------------------------------------------------------
-- 5. CRUD: TipoEstNom
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tipoestnom(p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipoEstNom (DescTEstNom, id_usuario) VALUES (p_desc, p_id_usu);
END; $$;

-- ----------------------------------------------------------
-- 6. CRUD: TipoParam
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tipoparam(p_desc VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipoParam (DescTParam, id_usuario) VALUES (p_desc, p_id_usu);
END; $$;

-- ----------------------------------------------------------
-- 7. CRUD: TipoPermiso
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tipopermiso(p_desc VARCHAR, p_acro VARCHAR, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipoPermiso (DescTPermiso, Acronimo, id_usuario) VALUES (p_desc, p_acro, p_id_usu);
END; $$;

-- ----------------------------------------------------------
-- 8. CRUD: TipAlcance
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_tipalcance(p_alcance VARCHAR, p_desc VARCHAR, p_id_per INTEGER, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO TipAlcance (Alcance, DescTAlcance, id_tpermiso, id_usuario) VALUES (p_alcance, p_desc, p_id_per, p_id_usu);
END; $$;

-- ----------------------------------------------------------
-- 9. CRUD: PerUsuario
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_perusuario(p_id_alcance INTEGER, p_id_usu_mod INTEGER, p_id_usu_own INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO PerUsuario (id_talcance, id_usuariomod, id_usuario) VALUES (p_id_alcance, p_id_usu_mod, p_id_usu_own);
END; $$;

-- ----------------------------------------------------------
-- 10. CRUD: Nominas (Tabla Principal)
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_nomina(
    p_anio INTEGER, p_mes INTEGER, p_nom INTEGER, p_fini DATE, p_ffin DATE, 
    p_id_tnom INTEGER, p_id_div INTEGER, p_dir VARCHAR, p_cod VARCHAR, p_id_usu INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO Nominas (Anio, mes, nomina, FechaInic, FechaFin, id_tiponom, id_Division, DireccionArch, CodigoSegSAT, id_usuario)
    VALUES (p_anio, p_mes, p_nom, p_fini, p_ffin, p_id_tnom, p_id_div, p_dir, p_cod, p_id_usu);
END; $$;

CREATE OR REPLACE PROCEDURE sp_actualizar_fechas_nomina(
    p_id INTEGER, p_xml TIMESTAMPTZ, p_sol TIMESTAMPTZ, p_tim TIMESTAMPTZ
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE Nominas SET FechaGenXML = p_xml, FechaSolTimb = p_sol, FechaTim = p_tim WHERE id_nomina = p_id;
END; $$;

-- ----------------------------------------------------------
-- 11. CRUD: EstatSATNom
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_estatsatnom(p_fcons TIMESTAMPTZ, p_id_est INTEGER, p_id_nom INTEGER, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO EstatSATNom (FechaCons, id_Est, id_nomina, id_usuario) VALUES (p_fcons, p_id_est, p_id_nom, p_id_usu);
END; $$;

-- ----------------------------------------------------------
-- 12. CRUD: LogProcesos
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_insertar_log(p_desc VARCHAR, p_id_nom INTEGER, p_id_usu INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO