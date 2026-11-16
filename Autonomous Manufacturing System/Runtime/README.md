# OpenPLC Runtime V4

## Development environment

- Docker Desktop on Windows
- Image: `ghcr.io/autonomy-logic/openplc-runtime:latest`
- Observed image ID (short): `378deec33b37`
- Container: `openplc-runtime`
- Editor HTTPS: `127.0.0.1:8443`
- Modbus TCP: `127.0.0.1:1502`
- Modbus server inside container: `0.0.0.0:1502`

## Restart an existing container

```powershell
docker start openplc-runtime
docker ps
```

If startup fails, inspect the logs:

```powershell
docker logs --tail 100 openplc-runtime
```

## Reproduce the environment

The image and published port bindings are confirmed from the development machine. The complete original container creation configuration (mounts, environment, restart policy, and image digest) has not yet been verified. Do not remove the existing container to perform these checks.

The `latest` image tag is mutable. Record the repository digest before treating the runtime setup as version-pinned.
