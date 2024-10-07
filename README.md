# Vue3 + FastAPI (Keycloak authentication)
This is template project:
  - Vue3 (Keycloak authentication with automatic refresh token)
  - FastAPI (Keycloak validate OAuth2 token)

Related environment configuration is automatically propagate to frontend.
If we don't want to use web-socket, set `SOCKET_DISABLED` to `True`.

## Keycloak configuration
- We have to enable "Implicit flow" and "Use refresh tokens"
- If the Keycloak is under reverse proxy we can not add "X-Frame-Options" header there.


## Devel
For development we can use docker-compose.yml, where Traefik covers all services to one entrypoint http://localhost:8000.
