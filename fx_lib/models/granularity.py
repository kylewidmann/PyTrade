from enum import Enum


class Granularity(Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"


MINUTES_MAP = {
    Granularity.M1: 1,
    Granularity.M5: 5,
    Granularity.M15: 15,
    Granularity.H1: 60,
    Granularity.H4: 240,
}
