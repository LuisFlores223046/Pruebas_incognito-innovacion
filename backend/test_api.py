"""
Script de pruebas completo — Mapa Interactivo CU UACJ
Ejecutar con el servidor corriendo: uvicorn app.main:app --reload
Uso: python test_api.py
"""
import requests
import json
import os
import time

BASE = "http://localhost:8000/api/v1"
TS = int(time.time())  # sufijo único por ejecución
TOKEN = None
HEADERS = {"Content-Type": "application/json"}

# IDs que se van guardando durante las pruebas
ids = {}

OK   = "✅"
FAIL = "❌"
SEP  = "─" * 60


def r(resp):
    """Imprime resultado de una petición."""
    icon = OK if resp.status_code < 400 else FAIL
    print(f"{icon} {resp.status_code}  {resp.request.method} {resp.request.url}")
    try:
        data = resp.json()
        print(json.dumps(data if not isinstance(data, list) else data[:2], indent=2, ensure_ascii=False)[:600])
    except Exception:
        print(resp.text[:300])
    print()
    return resp


def auth_headers():
    return {**HEADERS, "Authorization": f"Bearer {TOKEN}"}


# ══════════════════════════════════════════════════════════════
print(SEP)
print("1. SALUD DE LA API")
print(SEP)
r(requests.get("http://localhost:8000/"))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("2. CATEGORÍAS")
print(SEP)
resp = r(requests.get(f"{BASE}/categorias"))
if resp.ok and resp.json():
    ids["categoria_id"] = resp.json()[0]["id"]


# ══════════════════════════════════════════════════════════════
print(SEP)
print("3. EDIFICIOS")
print(SEP)
resp = r(requests.get(f"{BASE}/edificios"))
if resp.ok and resp.json():
    ids["edificio_id"] = resp.json()[0]["id"]


# ══════════════════════════════════════════════════════════════
print(SEP)
print("4. PISOS DE UN EDIFICIO")
print(SEP)
if "edificio_id" in ids:
    resp = r(requests.get(f"{BASE}/edificios/{ids['edificio_id']}/pisos"))
    if resp.ok and resp.json():
        ids["piso_id"] = resp.json()[0]["id"]


# ══════════════════════════════════════════════════════════════
print(SEP)
print("5. ESPACIOS — listado general")
print(SEP)
resp = r(requests.get(f"{BASE}/espacios"))
if resp.ok and resp.json():
    ids["espacio_id"] = resp.json()[0]["id"]

print("5b. Filtro por categoria_id")
r(requests.get(f"{BASE}/espacios", params={"categoria_id": ids.get("categoria_id", 1)}))

print("5c. Filtro por edificio_id")
r(requests.get(f"{BASE}/espacios", params={"edificio_id": ids.get("edificio_id", 1)}))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("6. BÚSQUEDA DE ESPACIOS")
print(SEP)
r(requests.get(f"{BASE}/espacios/buscar/biblioteca"))
r(requests.get(f"{BASE}/espacios/buscar/lab"))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("7. ESPACIOS ABIERTOS AHORA")
print(SEP)
r(requests.get(f"{BASE}/espacios/abiertos/ahora"))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("8. ESPACIOS CERCANOS (coordenadas del campus UACJ)")
print(SEP)
r(requests.get(f"{BASE}/espacios/cercanos", params={"lat": 31.7222, "lon": -106.4262, "radio": 500}))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("9. DETALLE COMPLETO DE UN ESPACIO (EspacioCompleto)")
print(SEP)
if "espacio_id" in ids:
    r(requests.get(f"{BASE}/espacios/{ids['espacio_id']}"))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("10. EVENTOS")
print(SEP)
resp = r(requests.get(f"{BASE}/eventos"))
if resp.ok and resp.json():
    ids["evento_id"] = resp.json()[0]["id"]

print("10b. Filtro por tipo")
r(requests.get(f"{BASE}/eventos", params={"tipo": "academico"}))

print("10c. Eventos de un espacio")
if "espacio_id" in ids:
    r(requests.get(f"{BASE}/espacios/{ids['espacio_id']}/eventos"))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("11. REPORTES — crear (ruta pública)")
print(SEP)
resp = r(requests.post(f"{BASE}/reportes", json={
    "espacio_id": ids.get("espacio_id", 1),
    "tipo": "sucio",
    "descripcion": "Prueba de reporte desde script",
}, headers=HEADERS))
if resp.ok:
    ids["reporte_id"] = resp.json()["id"]


# ══════════════════════════════════════════════════════════════
print(SEP)
print("12. AUTENTICACIÓN — login")
print(SEP)
resp = r(requests.post(f"{BASE}/auth/login", json={
    "username": "admin",
    "password": "admin123",
}, headers=HEADERS))

if resp.ok:
    TOKEN = resp.json()["access_token"]
    print(f"   Token obtenido: {TOKEN[:40]}...")
else:
    print(f"{FAIL} No se pudo obtener token. Deteniendo pruebas protegidas.")
    TOKEN = None

print()
print("12b. GET /auth/me")
if TOKEN:
    r(requests.get(f"{BASE}/auth/me", headers=auth_headers()))

print("12c. Endpoint protegido SIN token (debe devolver 401 o 403)")
resp = requests.get(f"{BASE}/auth/me")
icon = OK if resp.status_code in (401, 403) else FAIL
print(f"{icon} {resp.status_code}  GET /auth/me sin token → acceso denegado correctamente")
print()


# ══════════════════════════════════════════════════════════════
print(SEP)
print("13. CREAR ESPACIO (protegido)")
print(SEP)
if TOKEN:
    resp = r(requests.post(f"{BASE}/espacios", json={
        "codigo": f"TEST-{TS}",
        "nombre": "Espacio de Prueba Script",
        "categoria_id": ids.get("categoria_id"),
        "piso_id": ids.get("piso_id"),
        "latitud": 31.7220,
        "longitud": -106.4260,
        "notas": "Creado por test_api.py",
        "activo": True,
    }, headers=auth_headers()))
    if resp.ok:
        ids["nuevo_espacio_id"] = resp.json()["id"]


# ══════════════════════════════════════════════════════════════
print(SEP)
print("14. ACTUALIZAR ESPACIO (PATCH)")
print(SEP)
if TOKEN and "nuevo_espacio_id" in ids:
    r(requests.patch(f"{BASE}/espacios/{ids['nuevo_espacio_id']}", json={
        "notas": "Actualizado por test_api.py",
    }, headers=auth_headers()))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("15. CREAR EDIFICIO (protegido)")
print(SEP)
if TOKEN:
    resp = r(requests.post(f"{BASE}/edificios", json={
        "codigo": f"EDIF-{TS}",
        "nombre": "Edificio de Prueba",
        "descripcion": "Creado por test_api.py",
        "latitud": 31.7220,
        "longitud": -106.4260,
    }, headers=auth_headers()))
    if resp.ok:
        ids["nuevo_edificio_id"] = resp.json()["id"]

print("15b. ACTUALIZAR EDIFICIO (PATCH)")
if TOKEN and "nuevo_edificio_id" in ids:
    r(requests.patch(f"{BASE}/edificios/{ids['nuevo_edificio_id']}", json={
        "descripcion": "Actualizado por test_api.py",
    }, headers=auth_headers()))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("16. CREAR PISO (protegido)")
print(SEP)
if TOKEN and "nuevo_edificio_id" in ids:
    resp = r(requests.post(f"{BASE}/pisos", json={
        "edificio_id": ids["nuevo_edificio_id"],
        "numero": "PB",
    }, headers=auth_headers()))
    if resp.ok:
        ids["nuevo_piso_id"] = resp.json()["id"]


# ══════════════════════════════════════════════════════════════
print(SEP)
print("17. HORARIOS")
print(SEP)
if TOKEN and "nuevo_espacio_id" in ids:
    resp = r(requests.post(f"{BASE}/horarios", json={
        "espacio_id": ids["nuevo_espacio_id"],
        "dia_semana": 0,
        "hora_apertura": "08:00:00",
        "hora_cierre": "20:00:00",
    }, headers=auth_headers()))
    if resp.ok:
        ids["horario_id"] = resp.json()["id"]

    print("17b. PATCH horario")
    if "horario_id" in ids:
        r(requests.patch(f"{BASE}/horarios/{ids['horario_id']}", json={
            "hora_cierre": "21:00:00",
        }, headers=auth_headers()))

    print("17c. DELETE horario")
    if "horario_id" in ids:
        resp = requests.delete(f"{BASE}/horarios/{ids['horario_id']}", headers=auth_headers())
        icon = OK if resp.status_code == 204 else FAIL
        print(f"{icon} {resp.status_code}  DELETE /horarios/{ids['horario_id']}")
        print()


# ══════════════════════════════════════════════════════════════
print(SEP)
print("18. CONTACTOS")
print(SEP)
if TOKEN and "nuevo_espacio_id" in ids:
    resp = r(requests.post(f"{BASE}/contactos", json={
        "espacio_id": ids["nuevo_espacio_id"],
        "tipo": "correo",
        "valor": "prueba@uacj.mx",
    }, headers=auth_headers()))
    if resp.ok:
        ids["contacto_id"] = resp.json()["id"]

    print("18b. DELETE contacto")
    if "contacto_id" in ids:
        resp = requests.delete(f"{BASE}/contactos/{ids['contacto_id']}", headers=auth_headers())
        icon = OK if resp.status_code == 204 else FAIL
        print(f"{icon} {resp.status_code}  DELETE /contactos/{ids['contacto_id']}")
        print()


# ══════════════════════════════════════════════════════════════
print(SEP)
print("19. SERVICIOS")
print(SEP)
if TOKEN and "nuevo_espacio_id" in ids:
    resp = r(requests.post(f"{BASE}/servicios", json={
        "espacio_id": ids["nuevo_espacio_id"],
        "descripcion": "Servicio de prueba",
    }, headers=auth_headers()))
    if resp.ok:
        ids["servicio_id"] = resp.json()["id"]

    print("19b. DELETE servicio")
    if "servicio_id" in ids:
        resp = requests.delete(f"{BASE}/servicios/{ids['servicio_id']}", headers=auth_headers())
        icon = OK if resp.status_code == 204 else FAIL
        print(f"{icon} {resp.status_code}  DELETE /servicios/{ids['servicio_id']}")
        print()


# ══════════════════════════════════════════════════════════════
print(SEP)
print("20. FOTOS — subir, actualizar y eliminar")
print(SEP)
foto_espacio_id = ids.get("nuevo_espacio_id") or ids.get("espacio_id")
if TOKEN and foto_espacio_id:
    # Crear imagen de prueba de 1x1 pixel PNG (bytes mínimos válidos)
    PNG_1PX = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
        b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
        b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    img_path = "test_foto.png"
    with open(img_path, "wb") as f:
        f.write(PNG_1PX)

    print("20a. POST /fotos — subir imagen")
    with open(img_path, "rb") as f:
        resp = r(requests.post(
            f"{BASE}/fotos",
            data={
                "espacio_id": foto_espacio_id,
                "descripcion": "Foto de prueba",
                "es_principal": "false",
                "orden": "1",
            },
            files={"file": ("test_foto.png", f, "image/png")},
            headers={"Authorization": f"Bearer {TOKEN}"},
        ))
    if resp.ok:
        ids["foto_id"] = resp.json()["id"]

    print("20b. PATCH /fotos/{id} — actualizar metadatos")
    if "foto_id" in ids:
        r(requests.patch(f"{BASE}/fotos/{ids['foto_id']}", json={
            "descripcion": "Foto actualizada por test",
            "es_principal": True,
            "orden": 0,
        }, headers=auth_headers()))

    print("20c. DELETE /fotos/{id} — eliminar de Cloudinary y BD")
    if "foto_id" in ids:
        resp = requests.delete(f"{BASE}/fotos/{ids['foto_id']}", headers=auth_headers())
        icon = OK if resp.status_code == 204 else FAIL
        print(f"{icon} {resp.status_code}  DELETE /fotos/{ids['foto_id']}")
        print()

    # Limpiar imagen temporal
    if os.path.exists(img_path):
        os.remove(img_path)


# ══════════════════════════════════════════════════════════════
print(SEP)
print("21. EVENTOS (protegido)")
print(SEP)
if TOKEN:
    resp = r(requests.post(f"{BASE}/eventos", json={
        "titulo": "Evento de Prueba Script",
        "descripcion": "Creado por test_api.py",
        "fecha_inicio": "2026-05-01T10:00:00Z",
        "fecha_fin": "2026-05-01T18:00:00Z",
        "tipo": "academico",
        "espacio_id": ids.get("espacio_id"),
        "activo": True,
    }, headers=auth_headers()))
    if resp.ok:
        ids["nuevo_evento_id"] = resp.json()["id"]

    print("21b. PATCH evento")
    if "nuevo_evento_id" in ids:
        r(requests.patch(f"{BASE}/eventos/{ids['nuevo_evento_id']}", json={
            "descripcion": "Actualizado por test_api.py",
        }, headers=auth_headers()))

    print("21c. DELETE evento")
    if "nuevo_evento_id" in ids:
        resp = requests.delete(f"{BASE}/eventos/{ids['nuevo_evento_id']}", headers=auth_headers())
        icon = OK if resp.status_code == 204 else FAIL
        print(f"{icon} {resp.status_code}  DELETE /eventos/{ids['nuevo_evento_id']}")
        print()


# ══════════════════════════════════════════════════════════════
print(SEP)
print("22. REPORTES — listar y resolver (protegido)")
print(SEP)
if TOKEN:
    print("22a. Listar reportes pendientes")
    r(requests.get(f"{BASE}/reportes", params={"resuelto": "false"}, headers=auth_headers()))

    print("22b. Resolver reporte")
    if "reporte_id" in ids:
        r(requests.patch(f"{BASE}/reportes/{ids['reporte_id']}/resolver", headers=auth_headers()))


# ══════════════════════════════════════════════════════════════
print(SEP)
print("23. BORRADO LÓGICO DE ESPACIO (activo=False)")
print(SEP)
if TOKEN and "nuevo_espacio_id" in ids:
    resp = r(requests.delete(f"{BASE}/espacios/{ids['nuevo_espacio_id']}", headers=auth_headers()))
    if resp.ok:
        activo = resp.json().get("activo")
        icon = OK if activo is False else FAIL
        print(f"{icon} activo={activo}  (esperado: False — borrado lógico confirmado)")
        print()


# ══════════════════════════════════════════════════════════════
print(SEP)
print("PRUEBAS COMPLETADAS")
print(f"IDs generados durante la sesión: {ids}")
print(SEP)
