from . import start, analytics, help, support_author

all_routers = (
    start.router,
    analytics.router,
    help.router,
    support_author.router
)

__all__ = (
    "all_routers",
)
