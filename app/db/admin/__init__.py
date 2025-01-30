from fastapi import FastAPI
from sqladmin import Admin
from .views import UserView, UserStatsView, VideoStatsView
from .auth import authentication_backend
from app.db.base import engine


def attach_admin_panel(application: FastAPI):
    admin = Admin(application, engine, authentication_backend=authentication_backend)

    admin.add_view(UserView)
    admin.add_view(UserStatsView)
    admin.add_view(VideoStatsView)

