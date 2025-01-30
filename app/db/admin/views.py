from app.db.tables import User, UserStats, VideoStats
from sqladmin import ModelView


class UserView(ModelView, model=User):
    column_list = "__all__"
    column_searchable_list = [User.id, User.nickname]
    column_default_sort = [(User.id, True)]


class UserStatsView(ModelView, model=UserStats):
    column_list = "__all__"
    column_searchable_list = [UserStats.nickname]
    column_default_sort = [(UserStats.created_at, True)]


class VideoStatsView(ModelView, model=VideoStats):
    column_list = "__all__"
    column_searchable_list = [VideoStats.nickname]
    column_default_sort = [(VideoStats.created_at, True)]

