from enum import Enum
from typing import List, Dict, Text, Union
from pydantic import BaseModel, Field

class Format(str, Enum):
    # форматы записи ['standard', 'aside', 'chat', 'gallery', 'link', 'image', 'quote', 'status', 'video', 'audio']
    standard = 'standard'
    light = 'light'
    aside = 'aside'
    chat = 'chat'
    gallery = 'galerry'
    link = 'link'
    image = 'image'
    quote = 'quote'
    status = 'status'
    video = 'status'

class Status(str, Enum):
    # ['publish', 'future', 'draft', 'pending', 'private', 'acf-disabled']
    published = 'publish'
    future = 'future'
    draft = 'draft'
    pending = 'pending'
    private = 'private'
    unpublished = 'unpublish'
    trash = 'trash'

class Render(BaseModel):
    rendered : str

class Protected(Render):
    protected : str

class Post(BaseModel):
    id: int
    date : str
    date_gmt : str
    guid : Render
    modified : str
    modified_gmt : str
    slug : str
    status : Status
    type : str
    link : str
    title : Render
    content : Protected
    excerpt : Protected
    author : int
    featured_media : int
    comment_status : str  # должен быть enum
    ping_status : str  # должен быть enum
    sticky : bool  # False
    template : str
    format : Format
    meta : dict
    categories : list
    tags : list
    acf : dict
    _links : dict
