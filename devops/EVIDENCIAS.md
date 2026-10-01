# Evidencias DevOps

> Completar los enlaces o capturas después de ejecutar los pipelines y el despliegue en el entorno de entrega. No incluir tokens, contraseñas ni archivos `.env`.

## Matriz de cumplimiento

| Criterio | Implementación preparada | Evidencia pendiente |
| --- | --- | --- |
| Imagen Docker (15) | Build multi-etapa, usuario `appuser`, contexto reducido y sin secretos en capas | Build local/Actions y resultado del escaneo |
| Pipeline (30) | Pruebas antes del build, publicación solo desde `main`/tags, tags trazables y Trivy | Ejecuciones exitosas en Actions o Jenkins y Docker Hub |
| Defectos corregidos (20) | Defectos de root, trazabilidad, publicación, escaneo, configuración y probes documentados abajo | Revisión durante la sustentación |
| Despliegue k3s (25) | Configuración externa, probes, recursos, usuario no root y rolling update | Clúster Ready, pods, health y rollout |
| Evidencias y operación (10) | Checklist reproducible y comandos de verificación | Capturas/enlaces y prueba de rolling update |

## DevOps 1 — GitHub Actions → Docker Hub

- [ ] Workflow exitoso de lint y pruebas: _enlace a Actions_
- [ ] Build y escaneo Trivy exitosos: _enlace a Actions_
- [ ] Publicación desde `main`: _enlace a Actions / Docker Hub_
- [ ] Publicación de tag `vX.Y.Z`: _enlace a Actions / Docker Hub_
- [ ] Etiqueta SHA largo visible en Docker Hub: _enlace_

## DevOps 2 — Jenkins → Docker Hub

- [ ] Etapa de pruebas exitosa: _captura o enlace_
- [ ] Escaneo Trivy sin vulnerabilidades bloqueantes: _captura o enlace_
- [ ] Publicación desde `main` y tag: _captura o enlace_

## DevOps 3 — k3s

- [ ] `kubectl get nodes` muestra el nodo Ready: _captura_
- [ ] `kubectl -n demo get deploy,po,svc` muestra dos réplicas Ready: _captura_
- [ ] `GET /api/health/` responde `{"status":"ok","database":"ok"}`: _captura_
- [ ] `kubectl -n demo rollout status deployment/demo-backend`: _captura_
- [ ] Rolling update verificado sin caída usando una etiqueta nueva: _captura_

## Defectos corregidos

| Defecto de referencia | Corrección | Archivo |
| --- | --- | --- |
| Imagen Docker ejecutaba como root y no era multi-etapa | Runtime mínimo con usuario `appuser` y wheels separados | `backend/4-api/Dockerfile` |
| Dockerfile no definía un servidor de producción | Gunicorn con logs en stdout/stderr | `backend/4-api/Dockerfile` |
| Build/push no dependía de lint y pruebas | Jobs `quality` → `image` → `publish` | `.github/workflows/ci-dockerhub.yml` |
| Publicación sin control explícito de evento | Solo `main` y tags `vX.Y.Z`; PR no publica | `.github/workflows/ci-dockerhub.yml`, `Jenkinsfile` |
| Etiquetas poco trazables o mutables | Rama, semver, SHA largo y digest recomendado en k3s | CI y `devops/k8s/deployment.yaml` |
| No había escaneo de vulnerabilidades | Trivy bloquea HIGH/CRITICAL no corregidas | CI y `Jenkinsfile` |
| Secretos/configuración en el Deployment | ConfigMap y Secret referenciados por `envFrom` | `devops/k8s/*.yaml` |
| Solo había liveness, sin protección de tráfico | Readiness y liveness sobre `/api/health/` | `devops/k8s/deployment.yaml` |
| Deployment sin recursos ni estrategia segura | Requests/limits y rolling update `maxUnavailable: 0` | `devops/k8s/deployment.yaml` |
| Referencia usaba `DJANGO_SECRET_KEY`, pero Django lee `SECRET_KEY` | Nombre alineado con `config/settings.py` | `devops/k8s/secret.yaml` |
