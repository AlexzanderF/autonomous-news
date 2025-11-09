from enum import Enum

class SortField(str, Enum):
    """Fields available for sorting articles."""
    id = "id"                   # Sort by article ID (primary key)
    published_at = "published_at"  # Sort by publication date
    title = "title"             # Sort by article title
    created_at = "created_at"   # Sort by creation date


class SortOrder(str, Enum):
    """Sort order."""
    asc = "asc"    # Ascending order (A-Z, oldest first, 1-10)
    desc = "desc"  # Descending order (Z-A, newest first, 10-1)