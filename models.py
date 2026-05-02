"""
Task model and validation logic
Contains the Task class with validation methods
"""
from datetime import datetime


class Task:
    """Task model class with validation"""

    VALID_STATUS = {'Pending', 'In Progress', 'Done'}
    VALID_PRIORITY = {'Low', 'Medium', 'High'}

    def __init__(self, id=None, title='', description='', due_date='',
                 status='Pending', priority='Medium', created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.priority = priority
        self.created_at = created_at

    @staticmethod
    def validate(data, is_update=False):
        """
        Validate task data
        Returns (is_valid, errors)
        """
        errors = []

        title = data.get('title', '').strip() if data.get('title') else ''
        description = data.get('description', '').strip() if data.get('description') else ''
        due_date = data.get('due_date', '').strip() if data.get('due_date') else ''
        status = data.get('status', '').strip() if data.get('status') else ''
        priority = data.get('priority', '').strip() if data.get('priority') else ''

        if not title:
            errors.append('Title is required')
        elif len(title) < 3:
            errors.append('Title must be at least 3 characters')
        elif len(title) > 100:
            errors.append('Title must be 100 characters or less')

        if description and len(description) > 500:
            errors.append('Description must be 500 characters or less')

        if not due_date:
            errors.append('Due date is required')
        else:
            if not Task._is_valid_date(due_date):
                errors.append('Invalid date format. Use YYYY-MM-DD')
            else:
                try:
                    due = datetime.strptime(due_date, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    if due < today:
                        errors.append('Due date cannot be in the past')
                except ValueError:
                    pass

        if not status:
            errors.append('Status is required')
        elif status not in Task.VALID_STATUS:
            errors.append(f'Status must be one of: {", ".join(Task.VALID_STATUS)}')

        if not priority:
            errors.append('Priority is required')
        elif priority not in Task.VALID_PRIORITY:
            errors.append(f'Priority must be one of: {", ".join(Task.VALID_PRIORITY)}')

        return (len(errors) == 0, errors)

    @staticmethod
    def _is_valid_date(date_string):
        """Check if date string is valid YYYY-MM-DD format"""
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        """Create Task instance from dictionary"""
        return Task(
            id=data.get('id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            due_date=data.get('due_date', ''),
            status=data.get('status', 'Pending'),
            priority=data.get('priority', 'Medium'),
            created_at=data.get('created_at')
        )