import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class WorkoutSet:
    name: str
    description: Optional[str] = None
    code: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Exercise:
    name: str
    workoutset_code: uuid.UUID
    repeat_count: int
    round_count: int
    rest_seconds: int
    description: Optional[str] = None
    images: List[str] = field(default_factory=list)  # Относительные пути
    video_url: Optional[str] = None
    code: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserPrefs:
    default_repeat_count: int = 10
    default_round_count: int = 3
    default_rest_seconds: int = 60
    timer_sound: str = "default_sound.mp3" # Путь или идентификатор звука
    notifications_enabled: bool = True
    code: uuid.UUID = field(default_factory=uuid.uuid4) # Обычно одна запись на пользователя

@dataclass
class WorkoutLog:
    workoutset_code: uuid.UUID
    date: datetime = field(default_factory=datetime.now)
    duration_seconds: int = 0
    code: uuid.UUID = field(default_factory=uuid.uuid4)