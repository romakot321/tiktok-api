import datetime as dt
import uuid
from uuid import UUID
from enum import Enum

from sqlalchemy import BIGINT, bindparam
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy

from app.db.base import Base

sql_utcnow = text('(now() at time zone \'utc\')')


class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        letters = ['_' + i.lower() if i.isupper() else i for i in cls.__name__]
        return ''.join(letters).lstrip('_') + 's'

    id: M[int] = column(primary_key=True, index=True, autoincrement=True)
    created_at: M[dt.datetime] = column(server_default=sql_utcnow)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)


class User(BaseMixin, Base):
    nickname: M[str] = column(index=True, unique=True)
    app_id: M[str] = column(primary_key=True)
    app_bundle: M[str]
    avatar: M[str | None] = column(nullable=True)

    stats: M[list['UserStats']] = relationship(back_populates="user", lazy='noload', cascade='all, delete')
    video_stats: M[list['VideoStats']] = relationship(back_populates="user", lazy='noload', cascade='all, delete')
    __table_args__ = (
        UniqueConstraint('app_id', 'nickname', name='uix_externalid_appbundle'),
    )


class UserStats(BaseMixin, Base):
    followers: M[int] = column(type_=BIGINT)
    following: M[int] = column(type_=BIGINT)
    likes: M[int] = column(type_=BIGINT)
    diggs: M[int] = column(type_=BIGINT)
    nickname: M[str] = column(ForeignKey('users.nickname', ondelete="CASCADE"))

    user: M['User'] = relationship(back_populates='stats', lazy='noload')


class VideoStats(BaseMixin, Base):
    video_id: M[str]
    views: M[int] = column(type_=BIGINT)
    comments: M[int] = column(type_=BIGINT)
    diggs: M[int] = column(type_=BIGINT)
    shares: M[int] = column(type_=BIGINT)
    nickname: M[str] = column(ForeignKey('users.nickname', ondelete="CASCADE"))
    cover_url: M[str]
    video_url: M[str]

    user: M['User'] = relationship(back_populates='video_stats', lazy='noload')


class TrendVideo(BaseMixin, Base):
    cover_url: M[str]
    views: M[int] = column(type_=BIGINT)
    description: M[str]
    video_url: M[str]


class TrendHashtag(BaseMixin, Base):
    name: M[str]
    views: M[int] = column(type_=BIGINT)


class TrendSong(BaseMixin, Base):
    cover_url: M[str]
    song_url: M[str]
    title: M[str]
    author: M[str]

