from datetime import datetime


class Event:
    def __init__(
        self, id, user_id, name, description, date, location, creator_name=None
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.location = location
        self.creator_name = creator_name
        self.registrations = []

        # Set the date attribute
        if isinstance(date, datetime):
            # Already a datetime object
            self.date = date
        else:
            # String format - try to parse it
            try:
                # First try with seconds (database format)
                self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Then try without seconds (form format)
                self.date = datetime.strptime(date, "%Y-%m-%d %H:%M")

    @classmethod
    def from_dict(cls, data):
        """Create an Event object from a dictionary or sqlite3.Row"""
        event = cls(
            id=data["id"],
            user_id=data["user_id"],
            name=data["name"],
            description=data["description"],
            date=data["date"],
            location=data["location"],
            creator_name=data["creator_name"],
        )

        return event

    @classmethod
    def upcoming_events(cls, events):
        now = datetime.now()
        return [event for event in events if event.date >= now]
