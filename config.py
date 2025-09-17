import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("FNAF_Bot")

# ROOM_GRAPH: dict[Room, list[Room]] = {
ROOM_GRAPH: dict[str, list[str]] = {
    "main-stage": ["dining", "side-stage"],
    "side-stage": ["main-stage", "dining"],
    "kitchen": ["right-hall", "main-stage"],
    "dining": ["left-hall", "main-stage", "side-stage"],
    "left-hall": ["office", "dining", "kitchen"],
    "right-hall": ["office", "kitchen"],
    "office": [],
}
