from opencore.interface.api import app
from starlette.routing import Route, Mount

for route in app.routes:
    if isinstance(route, Route):
        print(f"Route: {route.path}")
    elif isinstance(route, Mount):
        print(f"Mount: {route.path} -> {route.app}")
