# Mapa Interactivo CU — UACJ · Backend

API REST para localizar espacios físicos dentro del Campus Ciudad Universitaria de la Universidad Autónoma de Ciudad Juárez.

## Stack

| Herramienta | Versión |
|-------------|---------|
| Python | 3.11+ |
| FastAPI | 0.111.x |
| SQLAlchemy | 2.0.x |
| Alembic | 1.13.x |
| PostgreSQL | 14+ |
| Pydantic | v2 |
| Uvicorn | 0.29.x |

---

## Instalación local

### 1. Clonar y entrar al directorio

```bash
git clone <repo-url>
cd mapacu-backend
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/MapaCU
SECRET_KEY=tu-clave-secreta-larga-y-aleatoria
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
FRONTEND_URL=http://localhost:5173
```

### 4. Aplicar migraciones

```bash
alembic upgrade head
```

### 5. Cargar datos de prueba

```bash
python seed.py
```

Esto crea:
- 22 categorías
- 5 edificios con pisos
- 10 espacios con horarios, servicios y fotos de placeholder
- Admin inicial: **username=admin / password=admin123**

### 6. Arrancar el servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`.
Documentación Swagger: `http://localhost:8000/docs`

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── main.py              ← FastAPI + CORS + routers
│   ├── database.py          ← SQLAlchemy session
│   ├── config.py            ← variables de entorno
│   ├── models/              ← 11 modelos ORM
│   ├── schemas/             ← 11 schemas Pydantic v2
│   ├── routers/             ← 10 routers FastAPI
│   ├── services/            ← lógica de negocio
│   └── auth/                ← JWT, bcrypt, dependencias
├── migrations/
│   └── versions/
│       └── 001_tablas_iniciales.py
├── seed.py
├── mock_data.json
├── requirements.txt
├── alembic.ini
├── render.yaml
├── Procfile
└── .env.example
```

---

## Endpoints principales

Todos bajo prefijo `/api/v1/`.

### Públicos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/categorias` | Lista todas las categorías |
| GET | `/edificios` | Lista todos los edificios |
| GET | `/edificios/{id}/pisos` | Pisos de un edificio |
| GET | `/espacios` | Espacios activos (filtros: `categoria_id`, `edificio_id`, `activo`) |
| GET | `/espacios/buscar/{q}` | Búsqueda por nombre/código/notas |
| GET | `/espacios/abiertos/ahora` | Espacios abiertos en este momento |
| GET | `/espacios/cercanos` | Por `lat`, `lon`, `radio` (metros) |
| GET | `/espacios/{id}` | Detalle completo con relaciones anidadas |
| GET | `/eventos` | Eventos activos (filtro: `tipo`) |
| GET | `/espacios/{id}/eventos` | Eventos de un espacio |
| POST | `/reportes` | Reportar un problema |

### Protegidos (JWT)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Obtener token (8 horas) |
| POST | `/auth/admin` | Crear administrador |
| GET | `/auth/me` | Perfil del admin autenticado |
| POST/PATCH/DELETE | `/espacios` | CRUD de espacios |
| POST/PATCH | `/edificios` | CRUD de edificios |
| POST | `/pisos` | Crear piso |
| POST/PATCH/DELETE | `/horarios` | CRUD de horarios |
| POST/DELETE | `/contactos` | CRUD de contactos |
| POST/DELETE | `/servicios` | CRUD de servicios |
| POST/PATCH/DELETE | `/fotos` | CRUD de fotos (Cloudinary) |
| POST/PATCH/DELETE | `/eventos` | CRUD de eventos |
| GET | `/reportes` | Listar reportes |
| PATCH | `/reportes/{id}/resolver` | Marcar reporte resuelto |

---

## Despliegue en Render

1. Hacer fork/push del repositorio a GitHub.
2. En [Render Dashboard](https://dashboard.render.com/) crear un nuevo **Web Service** apuntando al repo.
3. Render leerá `render.yaml` automáticamente y creará el servicio y la base de datos PostgreSQL.
4. En la sección **Environment** del servicio, agregar manualmente:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   - `FRONTEND_URL` (dominio del frontend en Render)
5. El primer deploy ejecutará `alembic upgrade head` automáticamente.
6. Correr el seed manualmente desde la consola de Render:
   ```bash
   python seed.py
   ```

---

## Autenticación

- JWT (HS256), expiración 8 horas.
- Enviar en header: `Authorization: Bearer <token>`.
- Bloqueo automático tras 5 intentos fallidos durante 15 minutos.

## Notas de diseño

- **Borrado lógico**: los espacios nunca se eliminan físicamente; `DELETE /espacios/{id}` pone `activo=False`.
- **Coordenadas**: sistema WGS84 (EPSG:4326), compatibles con OpenStreetMap/Leaflet.
- **Fechas**: siempre ISO 8601 con timezone UTC.
- **Categoría anidada**: el listado de espacios incluye `categoria` (nombre, icono, color_hex) para que Leaflet pinte marcadores sin una segunda petición.
