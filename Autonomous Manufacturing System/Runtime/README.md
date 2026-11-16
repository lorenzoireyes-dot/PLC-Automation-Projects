# OpenPLC Runtime V4.3.2

## Verified development environment

Docker Desktop on Windows, Linux AMD64 container, OpenPLC Runtime v4.3.2. The observed container was running and healthy after restart.

- Image: `ghcr.io/autonomy-logic/openplc-runtime:latest`
- Repository digest reported by Docker: `ghcr.io/autonomy-logic/openplc-runtime@sha256:378deec33b371eb09f8344e714d88b48efc7387f631f793371ba9f6a6e381c9f`
- Platform manifest digest: `sha256:7df7f9e956b1903bc7449aa5afd0a2d82914e92e5caa250755c0d6c77f39f821`
- Container: `openplc-runtime`
- Editor HTTPS: `127.0.0.1:8443`
- Modbus TCP: `127.0.0.1:1502`
- Modbus server inside container: `0.0.0.0:1502`
- Volume: `openplc-runtime-data:/var/run/runtime`
- Capabilities: SYS_NICE, SYS_RESOURCE
- Restart policy: no
- Logging driver: local
- Network: Docker bridge (Compose uses its own bridge network by default)
- Privileged mode: disabled

## Restart an existing container

```powershell
docker start openplc-runtime
docker ps
docker logs --tail 100 openplc-runtime
```

## Create a fresh runtime

Install Docker Desktop, enable Linux containers, and open a terminal in this directory. On a machine without an existing container of this name:

```powershell
docker compose pull
docker compose up -d
docker compose ps
```

The Compose configuration is reconstructed from the inspected container, not independently tested. If the reported repository digest cannot be pulled from the registry, verify the platform manifest digest or obtain the matching v4.3.2 image from the upstream project. Do not delete or replace an existing working container just to test these instructions.

## Deploy the PLC program

Open the native project in OpenPLC Editor V4 once all source files are present. Configure the runtime connection at localhost port 8443, authenticate with your own runtime credentials, build and deploy the program, and start PLC execution. The project contains the Modbus TCP server configuration. Confirm that the server listens on port 1502 before starting the HMI.

See [HMI instructions](../HMI/README.md) for Python setup and launch.

## Persistence and safety

The named volume retains runtime data. A fresh volume does not contain the deployed manufacturing program; deploy it separately. Do not publish credentials, remove the volume, or expose Modbus or the management API to external networks. This is a virtual automation demonstration, not a safety-rated industrial controller.

A healthy container confirms the runtime API is responding; it does not establish that the PLC program is executing or that the HMI is connected.
