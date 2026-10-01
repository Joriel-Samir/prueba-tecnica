# DevOps — Backend 4

Esta carpeta contiene la entrega de los retos DevOps sobre la API Django de `backend/4-api`.

## Estructura

- `../.github/workflows/ci-dockerhub.yml`: GitHub Actions para lint, pruebas, escaneo Trivy y publicación en Docker Hub.
- `../Jenkinsfile`: pipeline equivalente para Jenkins.
- `k8s/`: despliegue en k3s con configuración externa, probes, recursos y rolling update.
- `EVIDENCIAS.md`: checklist de ejecuciones y defectos corregidos.

## GitHub Actions

Configure en el repositorio espejo de GitHub los secrets `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`. El workflow ejecuta lint y pruebas antes de construir; las pull requests solo validan y las publicaciones ocurren en `main` o tags `vX.Y.Z`.

Las etiquetas publicadas incluyen rama, tag semántico, `latest` en `main` y SHA largo. No se usan credenciales en el YAML.

## Jenkins

Requisitos del agente:

1. Python 3.12, Docker y Trivy instalados.
2. PostgreSQL accesible en `127.0.0.1:5432` para la etapa de pruebas.
3. Credencial Jenkins de tipo Username with password con ID `dockerhub-creds`.
4. Pipeline multibranch configurado para descubrir `main` y tags.

El parámetro `DOCKERHUB_NAMESPACE` es público. El pipeline solo construye, escanea y publica desde `main` o un tag.

## k3s

1. Aplique `namespace.yaml`, `configmap.yaml` y un Secret creado desde la plantilla de `secret.yaml`.
2. Cambie en `deployment.yaml` el usuario de Docker Hub y use una etiqueta inmutable (idealmente un digest `@sha256:...`).
3. Aplique `deployment.yaml` y `service.yaml`.
4. Verifique `kubectl -n demo rollout status deployment/demo-backend` y acceda al NodePort `30080`.

Ejemplo para crear el Secret sin guardarlo en Git:

```bash
kubectl -n demo create secret generic demo-backend-secrets \
  --from-literal=SECRET_KEY='<valor-fuerte>' \
  --from-literal=DB_PASSWORD='<password-postgres>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

La aplicación necesita PostgreSQL. En este ejercicio el Deployment espera un servicio llamado `postgres`; puede ser PostgreSQL dentro del clúster o un endpoint externo ajustando el ConfigMap.
