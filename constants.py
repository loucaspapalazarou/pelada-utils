"""
AUTO-GENERATED FILE - DO NOT EDIT
Generated from pelada-common/schema/constants.json
Run: python pelada-common/generator/generate.py
"""

# Collection names
class Collections:
    USERS = "users"
    TEAMS = "teams"
    TEAMMEMBERS = "teamMembers"
    GAMES = "games"
    GAMEREQUESTS = "gameRequests"
    MESSAGES = "messages"
    VENUES = "venues"

# Team strength levels
class TeamStrengths:
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    PROFESSIONAL = "Professional"

    ALL = [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Professional",
    ]

# Team member states
class TeamMemberStates:
    ACTIVE = "active"
    PENDING = "pending"

# Game request statuses
class GameRequestStatuses:
    OPEN = "open"
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    REJECTED = "rejected"

# team field names
class TeamFields:
    NAME = "teamName"
    STRENGTH = "teamStrength"
    CAPTAIN = "captain"

# teamMember field names
class TeamMemberFields:
    USER = "user"
    TEAM = "team"
    STATE = "state"

# game field names
class GameFields:
    HOME_TEAM = "homeTeam"
    AWAY_TEAM = "awayTeam"
    VENUE = "venue"
    DATETIME_START = "datetimeStart"
    DATETIME_END = "datetimeEnd"

# gameRequest field names
class GameRequestFields:
    TEAM = "team"
    STATUS = "status"
    TIME_SLOTS = "timeSlots"
    VENUE = "venue"
    MATCHED_GAME_REQUEST = "matchedGameRequest"
    REJECTED_MATCHES = "rejectedMatches"

# message field names
class MessageFields:
    GAME = "game"
    SENDER = "sender"
    MESSAGE = "message"
