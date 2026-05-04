# Funcionalidad de correo (ChemClassify)

Documentación del envío de correo de prueba: comportamiento actual, archivos involucrados y el historial de enfoques que se probaron antes de consolidar **SMTP con Gmail y `smtplib`**.

---

## 1. Cómo funciona el sistema actual (para otro desarrollador)

### 1.1 Qué hace el sistema

Tras iniciar sesión con **Firebase Authentication** (correo institucional permitido por dominio), el usuario puede pulsar **«Send test email»** en la página **`/principal`**. La aplicación:

1. Comprueba que exista sesión (`uid` en la sesión Flask).
2. Toma el **correo del usuario autenticado** desde la sesión (`session['email']`), que coincide con el correo institucional del token de Firebase.
3. Llama a la lógica de negocio que envía **un solo correo de prueba** por SMTP a esa dirección (el usuario se envía el correo a sí mismo como comprobación de que el buzón SMTP del sistema funciona).

El correo sale del **remitente configurado en `.env`** (cuenta Gmail del sistema), no del correo institucional del alumno. El institucional es solo **destinatario**.

### 1.2 Flujo HTTP y de datos

| Paso | Componente | Descripción |
|------|--------------|-------------|
| 1 | `templates/PaginasSistema/principal.html` | Formulario `POST` a la ruta Flask `enviar_correo_prueba_vista`. |
| 2 | `LogicaMadre/LogicaFlask/ClasePrincipalFlask.py` | Ruta `POST /enviar-correo-prueba`: valida sesión, lee `session.get('email')`, llama `enviar_correo_prueba(destinatario)`. |
| 3 | `LogicaMadre/LogicaCorreo/ServicioCorreo.py` | Construye un `EmailMessage`, conecta al servidor SMTP (`smtplib`), autentica y envía. |
| 4 | Respuesta al usuario | Si todo va bien: `flash` de éxito y **redirección 302** a `/principal`. Si falla: `flash` con el mensaje de `ErrorEnvioCorreo`. |

No hay API JSON para este envío: el resultado se comunica con **mensajes flash** tras el redirect (comportamiento típico de formularios HTML en Flask).

### 1.3 Carga de configuración (`.env`)

Antes de leer variables, el módulo de correo importa:

- `Configuraciones/ConfiguracionCorreo/VariablesGraphCorreo.py`

Ese módulo (nombre histórico; ya no está ligado a Microsoft Graph) **carga el archivo `.env`** en la raíz del proyecto web (carpeta donde está `main.py`). Usa `python-dotenv` con **`override=True`** para que los valores del archivo **prevalezcan** sobre variables antiguas en el sistema operativo o en el IDE.

Variables relevantes para correo: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`. Plantilla: `env.graph.example`.

### 1.4 Detalle técnico del envío SMTP (`ServicioCorreo.py`)

- **Biblioteca:** `smtplib` + `ssl` + `email.message.EmailMessage`.
- **Puerto 587 (predeterminado):** conexión `SMTP`, `EHLO`, `STARTTLS`, `EHLO`, `login(usuario, contraseña)`, `send_message(mensaje)`.
- **Puerto 465:** se usa `SMTP_SSL` (TLS implícito desde el inicio).
- **Valores por defecto:** si no se define `SMTP_HOST`, se asume `smtp.gmail.com`; si no hay `SMTP_PORT`, `587`.
- **Remitente:** `SMTP_FROM` o, si falta, `SMTP_USER`.
- **Errores:** se encapsulan en `ErrorEnvioCorreo` con textos pensados para mostrarse en la interfaz; en fallos de autenticación SMTP se incluye, cuando el servidor lo devuelve, el código y mensaje (p. ej. `535 5.7.8` de Google).

### 1.5 Requisitos típicos con Gmail

- Cuenta Google con **verificación en dos pasos** activada.
- **Contraseña de aplicación** de 16 caracteres (sin espacios en `.env`) asociada a esa misma cuenta que `SMTP_USER`.
- `SMTP_USER` debe ser **exactamente** el correo de la cuenta donde se generó la contraseña de aplicación.

### 1.6 Entrega a buzones institucionales

Una vez Gmail acepta el mensaje (sin excepción en Python), la entrega en `@ucundinamarca.edu.co` depende del **servidor de correo de la universidad** (filtros, cuarentena, correo no deseado, retrasos). Si la aplicación muestra éxito y el mensaje aparece en **Enviados** de Gmail, el cliente SMTP cumplió su parte; conviene revisar carpeta de spam o pedir trazabilidad a TI si no llega al buzón.

---

## 2. Historial de intentos y decisiones

### 2.1 Microsoft Azure / Microsoft Graph (credenciales de cliente)

**Enfoque:** OAuth2 con **credenciales de cliente** (aplicación daemon) contra Microsoft Graph, endpoint `POST .../v1.0/users/{remitente}/sendMail`, permiso de aplicación **`Mail.Send`**, variables `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET` y remitente en el inquilino de Entra ID.

**Problemas encontrados:**

- **`HTTP 401`** al llamar a `sendMail` cuando el remitente por defecto era una dirección **@outlook.com** de consumidor mientras el registro de aplicación y el token pertenecían al **inquilino institucional**. Con permisos de **aplicación**, el buzón desde el que se envía debe existir **en ese mismo inquilino** (Microsoft 365 / Exchange Online), no una cuenta personal ajena al tenant.
- Confusión habitual entre **inicio de sesión del usuario en la web** (Firebase, correo `@ucundinamarca.edu.co`) y **identidad del remitente SMTP/Graph** (cuenta de servicio en Azure).

**Conclusión:** Válido para escenarios «todo Microsoft 365 en un solo tenant» con buzón de servicio y administrador que otorgue consentimiento. No encajaba con el objetivo de usar una **cuenta personal de sistema** (@outlook.com / fuera del tenant) como remitente sin buzón homologado en el tenant.

### 2.2 Microsoft Graph «delegado» y SMTP Outlook.com (cuenta personal)

**Enfoque intermedio (ya retirado del código):**

- **Graph delegado:** `POST /me/sendMail` con **refresh token** y aplicación registrada para cuentas personales Microsoft (`consumers`), script de ayuda para flujo por código en dispositivo.
- **SMTP** contra `smtp-mail.outlook.com` con usuario/contraseña o contraseña de aplicación.

**Problemas:**

- **Outlook.com / SMTP:** Microsoft suele **rechazar la autenticación básica** (`SMTPAuthenticationError`) en cuentas personales; las políticas actuales empujan a OAuth2 para SMTP/IMAP.
- **Graph delegado:** exige mantener **refresh token** y registro de app en Azure; más operativo que SMTP Gmail con contraseña de aplicación para un proyecto académico.

**Conclusión:** Tecnicamente viable con más trabajo operativo (tokens, Azure). Se descartó a favor de una sola vía **SMTP + Gmail** más simple de configurar en `.env`.

### 2.3 SendGrid (y proveedores similares)

**Consideración:** Servicios transaccionales (SendGrid, Mailgun, Amazon SES, etc.) envían con **API key** y remitente verificado en un dominio; permiten entregar a cualquier dirección válida una vez superado el modo sandbox y la reputación.

**Por qué no se adoptó (por ahora):** el equipo prefirió no depender de un tercero de pago/cuenta adicional y alinearse con una **cuenta Gmail del proyecto** bajo control directo. SendGrid sigue siendo una opción razonable si en el futuro se requiere mayor volumen, analíticas o dominio propio (`noreply@proyecto.edu`).

### 2.4 Solución adoptada: `smtplib` + Gmail

**Enfoque actual:** conexión estándar a `smtp.gmail.com`, puerto 587, STARTTLS, autenticación con **usuario Gmail + contraseña de aplicación**.

**Ventajas para el proyecto:**

- Sin Azure ni Graph en el código de envío.
- Configuración acotada a variables en `.env`.
- Mismo patrón que tutoriales clásicos de Python (con las salvedades actuales de Google: 2FA y contraseña de aplicación).

**Limitaciones a tener en cuenta:**

- Límites de envío y políticas antispam de Google.
- Cuentas **Google Workspace** pueden tener SMTP restringido por administración.
- Las contraseñas de aplicación **no** deben versionarse; `.env` debe permanecer en `.gitignore`.

---

## 3. Resumen de archivos clave

| Archivo | Rol |
|---------|-----|
| `LogicaMadre/LogicaCorreo/ServicioCorreo.py` | Envío SMTP; `enviar_correo_prueba`, `ErrorEnvioCorreo`. |
| `LogicaMadre/LogicaFlask/ClasePrincipalFlask.py` | Ruta `POST /enviar-correo-prueba` y mensajes flash. |
| `Configuraciones/ConfiguracionCorreo/VariablesGraphCorreo.py` | Carga de `.env` (nombre de archivo heredado). |
| `Configuraciones/ConfiguracionCorreo/CorreoSistemaOutlook.py` | Notas de configuración; el remitente efectivo es `.env`. |
| `env.graph.example` | Plantilla de variables SMTP (y comentarios). |
| `.env` | Valores reales (no subir a git). |

---

## 4. Dependencias

El envío de correo usa solo la **biblioteca estándar** de Python (`smtplib`, `ssl`, `email`). La dependencia **`python-dotenv`** (en `requirements.txt`) facilita la carga de `.env`; si no estuviera instalada, el proyecto usa un lector mínimo integrado en `VariablesGraphCorreo.py`.

**Nota:** En su momento existía la dependencia **`msal`** para Graph; se eliminó al consolidar solo SMTP.

---

*Documento alineado con el comportamiento del código en el repositorio. Si se reintroduce otro transporte (Graph, SendGrid, etc.), conviene actualizar esta página y la sección 1.*
