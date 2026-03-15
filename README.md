# Business Security API

Microservicio de autenticacion y autorizacion para **Business ERP**, desarrollado con FastAPI y SQLAlchemy. Gestiona usuarios, perfiles, empleados y el menu jerarquico del sistema. Expone una API REST documentada automaticamente con OpenAPI/Swagger.

---

## Lenguaje y Stack Tecnologico

| Capa | Tecnologia | Version |
|------|-----------|---------|
| Lenguaje | **Python** | 3.x (>= 3.10 recomendado) |
| Framework web | **FastAPI** | 0.109.0 |
| Servidor ASGI | **uvicorn** | 0.27.0 |
| ORM | **SQLAlchemy** | 2.0.25 |
| Migraciones BD | **Alembic** | 1.13.1 |
| Driver PostgreSQL | **psycopg (v3)** | 3.1.18 |
| Validacion datos | **Pydantic v2** | 2.5.3 |
| Autenticacion JWT | **python-jose** | 3.3.0 |
| Hash contrasenas | **bcrypt + passlib** | 4.0.1 / 1.7.4 |
| Variables entorno | **python-dotenv** | 1.0.0 |
| Base de datos | **PostgreSQL** | >= 13 |

---

## Caracteristicas

- **Autenticacion JWT** con expiracion configurable
- **Control de intentos fallidos** — bloqueo automatico tras N intentos
- **Gestion de usuarios** con estados (Activo, Inactivo, Bloqueado)
- **Perfiles y roles** — asignacion de menus por perfil
- **Menu jerarquico** — arbol recursivo segun el perfil del usuario autenticado
- **Gestion de empleados** con busqueda por cedula
- **Swagger UI** automatico en `/docs` (incluido por FastAPI)
- **Migraciones de BD** con Alembic
- **CORS** configurable por entorno

---

## Estructura del Proyecto

```
Business-Security/
├── app/
│   ├── main.py                # Punto de entrada FastAPI
│   ├── core/
│   │   ├── config.py          # Configuracion (Pydantic Settings)
│   │   ├── security.py        # JWT, password hashing
│   │   └── dependencies.py    # Dependencias inyectables (DB session, auth)
│   ├── db/
│   │   ├── session.py         # Engine y SessionLocal
│   │   └── models/            # Modelos SQLAlchemy
│   │       ├── estado.py
│   │       ├── empleados.py
│   │       ├── usuarios.py
│   │       ├── perfil.py
│   │       └── menu.py
│   ├── routers/               # Endpoints (FastAPI APIRouter)
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── perfiles.py
│   │   ├── empleados.py
│   │   └── menu.py
│   ├── schemas/               # Schemas Pydantic (request/response)
│   └── services/              # Logica de negocio
├── alembic/                   # Migraciones de base de datos
├── alembic.ini
├── init_db.py                 # Script de inicializacion de tablas
├── seed_db.py                 # Script para poblar datos iniciales
├── check_db_sqlalchemy.py     # Verificar conexion a la BD
├── requirements.txt           # Dependencias Python
├── .env                       # Variables de entorno (no commitear)
├── run_server.ps1             # Script PowerShell para iniciar el servidor
└── README.md
```

---

## Instalacion

### Requisitos previos

- Python >= 3.10
- PostgreSQL >= 13 corriendo localmente
- Base de datos `Auth` creada en PostgreSQL

### 1. Crear entorno virtual

```powershell
cd C:\Proyectos\BusinessApp\Business-Security
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```powershell
copy .env.example .env
```

Editar `.env` con tus valores:

```env
# Conexion PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:tu_password@localhost:5432/Auth

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=Business Security API
APP_VERSION=1.0.0
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:4000

# Seguridad login
MAX_LOGIN_ATTEMPTS=3
```

> La `SECRET_KEY` debe ser identica a la configurada en **Business-Gateway**.

### 4. Inicializar la base de datos

#### Opcion A: Base de datos nueva (tablas inexistentes)

```powershell
# Aplicar migraciones (crea todas las tablas)
alembic upgrade head

# Crear datos iniciales (estados, perfiles, admin)
python seed_db.py
```

#### Opcion B: Base de datos PostgreSQL existente con tablas ya creadas

```powershell
# Verificar conexion
python check_db_sqlalchemy.py

# Sincronizar Alembic con el estado actual sin re-crear tablas
alembic stamp head

# (Opcional) Poblar datos si la BD esta vacia
python seed_db.py
```

**Credenciales de prueba generadas por seed_db.py:**

| Usuario | Contrasena |
|---------|-----------|
| `admin` | `admin123` |
| `usuario` | `usuario123` |

---

## Levantar el Microservicio

### Desarrollo (con auto-reload)

```powershell
# 1. Activar entorno virtual (si no esta activo)
cd C:\Proyectos\BusinessApp\Business-Security
.venv\Scripts\Activate.ps1

# 2. Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### Usando el script incluido

```powershell
cd C:\Proyectos\BusinessApp\Business-Security
.\run_server.ps1
```

### Produccion

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servidor estara disponible en `http://localhost:8000`.

### Verificar que esta corriendo

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
# Respuesta esperada: @{status=ok}
```

---

## URLs Disponibles

| URL | Descripcion |
|-----|-------------|
| `http://localhost:8000/` | Root — info basica del servicio |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/docs` | Swagger UI interactivo |
| `http://localhost:8000/redoc` | ReDoc (documentacion alternativa) |
| `http://localhost:8000/openapi.json` | Spec OpenAPI 3.0 en JSON |

---

## Endpoints de la API

### Autenticacion (`/api/auth`)

| Metodo | Ruta | Auth | Descripcion |
|--------|------|------|-------------|
| POST | `/api/auth/login` | No | Login con usuario y contrasena |
| POST | `/api/auth/login-form` | No | Login en formato OAuth2 form |
| GET | `/api/auth/me` | JWT | Datos del usuario autenticado |
| POST | `/api/auth/change-password` | JWT | Cambiar contrasena |
| POST | `/api/auth/reset-attempts/{id}` | JWT | Resetear intentos fallidos |

### Empleados (`/api/empleados`)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/empleados/` | Listar todos los empleados |
| GET | `/api/empleados/{id}` | Obtener empleado por ID |
| GET | `/api/empleados/cedula/{cedula}` | Buscar empleado por cedula |
| POST | `/api/empleados/` | Crear empleado |
| PUT | `/api/empleados/{id}` | Actualizar empleado |
| DELETE | `/api/empleados/{id}` | Eliminar empleado |

### Usuarios (`/api/usuarios`)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/usuarios/` | Listar usuarios |
| GET | `/api/usuarios/{id}` | Obtener usuario |
| POST | `/api/usuarios/` | Crear usuario |
| PUT | `/api/usuarios/{id}` | Actualizar usuario |
| DELETE | `/api/usuarios/{id}` | Eliminar usuario |

### Perfiles (`/api/perfiles`)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/perfiles/` | Listar perfiles |
| GET | `/api/perfiles/{id}` | Obtener perfil |
| POST | `/api/perfiles/` | Crear perfil |
| PUT | `/api/perfiles/{id}` | Actualizar perfil |
| POST | `/api/perfiles/{id}/menus` | Asignar menus al perfil |

### Menu (`/api/menu`)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/menu/tree` | Arbol de menu del usuario autenticado |
| GET | `/api/menu/` | Listar todos los menus |
| POST | `/api/menu/` | Crear elemento de menu |
| PUT | `/api/menu/{id}` | Actualizar elemento de menu |

---

## Flujo de Autenticacion

### 1. Login

```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' `
  -Method Post -ContentType 'application/json' `
  -Body '{"usuario":"admin","contrasenia":"admin123"}'
```

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Usar el token

Incluir el token en el header de cada peticion autenticada:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Obtener datos del usuario actual

```powershell
$token = "eyJhbGciOiJIUzI1..."
Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/me' `
  -Headers @{ Authorization = "Bearer $token" }
```

---

## Modelo de Datos

### Tablas principales

| Tabla | Descripcion |
|-------|-------------|
| `estado` | Estados del sistema (Activo, Inactivo, Bloqueado) |
| `empleados` | Informacion personal de empleados |
| `usuarios` | Credenciales, perfil y estado de acceso |
| `perfil` | Roles/perfiles de usuario |
| `menu` | Elementos de menu (estructura jerarquica recursiva) |
| `perfil_menu` | Relacion N:N entre perfiles y menus |

---

## Migraciones con Alembic

```powershell
# Crear nueva migracion tras modificar un modelo
alembic revision --autogenerate -m "descripcion del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Revertir ultima migracion
alembic downgrade -1

# Ver estado actual
alembic current

# Ver historial de migraciones
alembic history
```

Para el flujo completo con base de datos existente, consultar [MIGRACIONES.md](./MIGRACIONES.md).

---

## Swagger UI

FastAPI genera la documentacion OpenAPI automaticamente a partir de los decoradores de rutas, schemas Pydantic y type hints. No requiere configuracion adicional.

Para acceder:
1. Levantar el servidor (`uvicorn app.main:app --reload --port 8000`)
2. Abrir `http://localhost:8000/docs`
3. Usar el boton **Authorize** para ingresar el JWT y probar endpoints protegidos

---

## Seguridad

- Contrasenas hasheadas con **bcrypt** (factor de costo configurable)
- Tokens JWT firmados con HS256, expiracion configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Bloqueo automatico** tras `MAX_LOGIN_ATTEMPTS` intentos fallidos consecutivos
- Estados de usuario: Activo / Inactivo / Bloqueado
- CORS restringido a origenes configurados en `.env`

---

## Configuracion de Produccion

1. Cambiar `SECRET_KEY` a un valor seguro generado aleatoriamente
2. Configurar `DEBUG=False`
3. Usar PostgreSQL (no SQLite)
4. Ajustar `ALLOWED_ORIGINS` con dominios reales
5. Correr detras del API Gateway (Business-Gateway en puerto 4000)
6. Usar HTTPS en el gateway
7. Incrementar `workers` en uvicorn segun carga esperada

---

## Licencia

Proyecto interno — Business ERP.
