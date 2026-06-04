# time-bot-public

Este repositorio contiene un disparador seguro para ejecutar un workflow de GitHub Actions en un repositorio de destino configurable.

## ¿Qué hay aquí?

- `.github/workflows/trigger-private.yml`: workflow activo que ejecuta `scripts/dispatch_private_workflow.py` usando el secreto `PRIVATE_REPO_TOKEN`.
- `scripts/dispatch_private_workflow.py`: script Python parametrizable y seguro para disparar workflows desde un entorno local o CI.
- `requirements.txt`: dependencias mínimas necesarias para el script.
- `.gitignore`: evita subir entornos virtuales, archivos temporales y datos sensibles.

## Requisitos

- Python 3.9 o superior.
- Un token de GitHub con permisos de `repo` y `workflow` en el repositorio de destino.

## Configuración recomendada

1. Guarda el token como secreto en GitHub Actions (`PRIVATE_REPO_TOKEN`) o como variable de entorno local.
2. Si deseas cambiar el repositorio o workflow de destino sin editar el código, usa variables de entorno o argumentos CLI:
   - `GITHUB_OWNER`
   - `GITHUB_REPO`
   - `GITHUB_WORKFLOW_FILE`
   - `GITHUB_BRANCH`
   - `GITHUB_API_URL` (opcional)
3. Instala dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Uso local

Ejemplo mínimo:

```bash
export PRIVATE_REPO_TOKEN="tu_token_secreto"
python scripts/dispatch_private_workflow.py
```

Ejemplo con valores explícitos:

```bash
export PRIVATE_REPO_TOKEN="tu_token_secreto"
python scripts/dispatch_private_workflow.py \
  --owner your-owner \
  --repo your-repo \
  --workflow your-workflow.yml \
  --branch main
```

También puedes usar variables de entorno en lugar de pasar los argumentos manualmente:

```bash
export PRIVATE_REPO_TOKEN="tu_token_secreto"
export GITHUB_OWNER="your-owner"
export GITHUB_REPO="your-repo"
export GITHUB_WORKFLOW_FILE="your-workflow.yml"
export GITHUB_BRANCH="main"
python scripts/dispatch_private_workflow.py
```

## Buenas prácticas aplicadas

- Mantén el token en un secreto de GitHub Actions (`PRIVATE_REPO_TOKEN`) o en una variable de entorno del entorno de ejecución; nunca lo pongas en el repositorio ni en el código.
- Usa variables de entorno o argumentos CLI para configurar `owner`, `repo`, `workflow` y `branch`, en lugar de hardcodear valores sensibles o específicos del entorno.
- Limita los permisos del token al mínimo necesario (`repo` y `workflow`) y rota el token si se expone.
- Usa `requests.post(..., timeout=30)` para evitar bloqueos indefinidos.
- Evita imprimir el cuerpo completo de la respuesta HTTP para no filtrar información sensible en logs.
- Añade `X-GitHub-Api-Version` y valida los códigos de estado HTTP para detectar errores de forma clara.
- En CI, usa secretos del runner y no valores fijos dentro del YAML.

## Seguridad

- No compartas ni registres el token en logs, artefactos ni archivos versionados.
- Usa `.gitignore` para evitar subir entornos virtuales y archivos temporales.
- Si el repositorio de destino es privado o usa GitHub Enterprise, define `GITHUB_API_URL` explícitamente.
- Revisa periódicamente que el token tenga los permisos adecuados y revoca cualquier credencial comprometida.
