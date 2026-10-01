# Evidencias DevOps

> Completar los enlaces o capturas después de ejecutar los pipelines y el despliegue en el entorno de entrega. No incluir tokens, contraseñas ni archivos `.env`.

## Matriz de cumplimiento

| Criterio | Implementación preparada | Evidencia pendiente |
| --- | --- | --- |
| Imagen Docker (15) | Build multi-etapa, usuario `appuser`, contexto reducido y sin secretos en capas | Build local/Actions y resultado del escaneo verificados |
| Pipeline (30) | Pruebas antes del build, publicación solo desde `main`/tags, tags trazables y Trivy | Ejecuciones exitosas en Actions o Jenkins y Docker Hub |
| Defectos corregidos (20) | Defectos de root, trazabilidad, publicación, escaneo, configuración y probes documentados abajo | Revisión durante la sustentación |
| Despliegue k3s (25) | Configuración externa, probes, recursos, usuario no root y rolling update | Verificado en k3d local; imagen fijada por digest |
| Evidencias y operación (10) | Checklist reproducible y comandos de verificación | Health, recursos, rollout y capturas documentados |

## DevOps 1 — GitHub Actions → Docker Hub

- [x] Lint y pruebas exitosos: [job de Lint and tests](https://github.com/Joriel-Samir/prueba-tecnica/actions/runs/36803766957/job/110183566260)
- [x] Build y escaneo Trivy exitosos: [job de Build and scan image](https://github.com/Joriel-Samir/prueba-tecnica/actions/runs/36803766957/job/110183790867)
- [x] Publicación exitosa: [job de Publish immutable tags](https://github.com/Joriel-Samir/prueba-tecnica/actions/runs/36803766957/job/110183985038)
- [x] Publicación visible en Docker Hub: [jorielsamir/actividades-api](https://hub.docker.com/r/jorielsamir/actividades-api/tags)
- [x] Tag semántico `v1.0.1` visible en Docker Hub.
- [x] Tag semántico final `v1.0.2` visible en Docker Hub.
- [x] Tag SHA `sha-c6ee63b6261f795d61b30ed4c881700743de554b` visible en Docker Hub.

### Evidencia de etiquetas publicadas

| Etiqueta | Digest visible | Interpretación |
| --- | --- | --- |
| `latest` | `5565a33e3682` | Última imagen publicada |
| `v1.0.1` | `5565a33e3682` | Versión semántica reproducible |
| `sha-c6ee63b6261f795d61b30ed4c881700743de554b` | `5565a33e3682` | Commit exacto de origen |
| `main` | `f961ae605e32` | Imagen previa de la rama principal |

Las tres primeras etiquetas apuntan al mismo digest; son referencias diferentes de
la misma imagen y no copias duplicadas. El Deployment de k3d usa el digest completo
`sha256:fcd3a54d7578f1874c19f7ecdf246eb1129ed85fd1886b6f62ff5cf0b9f6e917`.
La captura de la pestaña **Tags** de Docker Hub se conserva como evidencia visual.


### Capturas adjuntas

![Docker Hub: vista del repositorio](evidencias/Screenshot%202026-09-30%20200225.png)

![Docker Hub: tags latest y SHA](evidencias/Screenshot%202026-09-30%20200256.png)

![Docker Hub: tags v1.0.1 y main](evidencias/Screenshot%202026-09-30%20200325.png)

![Docker Hub: tags de la entrega final v1.0.2](evidencias/Screenshot%202026-09-30%20210259.png)

![Docker Hub: digest de la entrega final v1.0.2](evidencias/Screenshot%202026-09-30%20210329.png)

## DevOps 2 — Jenkins → Docker Hub

- [ ] Etapa de pruebas exitosa: _captura o enlace_
- [ ] Escaneo Trivy sin vulnerabilidades bloqueantes: _captura o enlace_
- [ ] Publicación desde `main` y tag: _captura o enlace_

## DevOps 3 — k3s

- [x] `kubectl get nodes` muestra los nodos `k3d-ihungo-agent-0` y `k3d-ihungo-server-0` en `Ready`.
- [x] `kubectl -n demo get deploy,po,svc` muestra `demo-backend 2/2`, PostgreSQL `1/1` y NodePort `30080`.
- [x] `GET /api/health/` responde `{"status":"ok","database":"ok"}` después de ejecutar las migraciones.
- [x] `kubectl -n demo rollout status deployment/demo-backend` terminó con `successfully rolled out`.
- [x] Rolling update verificado cambiando temporalmente `v1.0.1` a `main` y restaurando `v1.0.1`; ambos rollouts terminaron correctamente y health siguió en `ok`.

La evidencia de terminal se capturará en la sustentación. El PostgreSQL usado para esta
prueba corre como `StatefulSet` dentro de `demo`; su contraseña se creó mediante un
Secret de Kubernetes y no se guardó en Git.

### Capturas de k3d y API

![Nodos k3d en estado Ready](evidencias/Screenshot%202026-09-30%20203428.png)

![Deployment, pods y Services](evidencias/Screenshot%202026-09-30%20203718.png)

![Endpoint de salud de la API](evidencias/Screenshot%202026-09-30%20204255.png)

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
| La referencia no incluía PostgreSQL reproducible para k3s | StatefulSet con volumen persistente, probes y credenciales externas | `devops/k8s/postgres.yaml` |
