"""Types for representing subjects"""


class Subject:
    """
    Class representing a measurement subject.

    Attributes:
        key (str): The key how the subject is referenced in measures.
        description (str): Description of the subject.
    """

    def __init__(self, key, description=""):
        self.key = key
        self.description = description

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


SUBJECT_PROCESS = Subject(key='process', description="The current running process.")
SUBJECT_CHILDREN = Subject(
    key='children',
    description="The aggregate of all children of the running process.",
)
