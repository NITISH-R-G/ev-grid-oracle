try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:  # pragma: no cover
    raise ImportError("openenv-core required. Install deps from pyproject.") from e

from ev_grid_oracle.models import EVGridAction, EVGridObservation
from server.ev_grid_environment import EVGridEnvironment


app = create_app(
    EVGridEnvironment,
    EVGridAction,
    EVGridObservation,
    env_name="ev-grid-oracle",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

