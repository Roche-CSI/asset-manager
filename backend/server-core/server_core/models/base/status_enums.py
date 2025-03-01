class StatusEnums:
    PUBLIC = 1
    PRIVATE = 2
    DELETED = 3
    DEPRECATED = 4
    OBSOLETE = 5
    ARCHIVE_FLAGGED = 6
    ARCHIVED = 7

    @classmethod
    def from_string(cls, value):
        """
        Convert a string to its corresponding numeric value.
        Accepts both the string representation of the number or the status name.
        """
        try:
            # Try to convert to int directly
            return int(value)
        except ValueError:
            # If not a number, try to match the name
            status_name = value.upper()
            for name, num_value in cls.__dict__.items():
                if name.isupper() and name == status_name:
                    return num_value
            raise ValueError(f"'{value}' is not a valid status")

    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid status value."""
        if isinstance(value, str):
            try:
                cls.from_string(value)
                return True
            except ValueError:
                return False
        return value in cls.__dict__.values()

# Usage examples
if __name__ == "__main__":
    # Direct access to status values
    print(StatusEnums.PUBLIC)  # 1
    print(StatusEnums.PRIVATE)  # 2

    # Converting from string
    print(StatusEnums.from_string("1"))  # 1
    print(StatusEnums.from_string("PUBLIC"))  # 1
    print(StatusEnums.from_string("PRIVATE"))  # 2

    # Validation
    print(StatusEnums.is_valid(1))  # True
    print(StatusEnums.is_valid("PUBLIC"))  # True
    print(StatusEnums.is_valid(6))  # False
    print(StatusEnums.is_valid("INVALID"))  # False

    # Error handling
    try:
        StatusEnums.from_string("INVALID")
    except ValueError as e:
        print(e)  # "'INVALID' is not a valid status"