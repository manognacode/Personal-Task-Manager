function getApiBase() {
    const currentPort = window.location.port;
    const serverPort = window.SERVER_PORT || 8000;
    if (String(currentPort) === String(serverPort)) {
        return '/api';
    }
    return `http://localhost:${serverPort}/api`;
}

const API_BASE = getApiBase();
let isEditing = false;

console.log('Task Manager app.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready, loading data...');
    loadDashboard();
    loadTasks();

    document.getElementById('task-due-date').addEventListener('change', function() {
        const today = new Date().toISOString().split('T')[0];
        if (this.value && this.value < today) {
            showFieldError('task-due-date', 'due-date-error', 'Cannot select past date');
            this.value = '';
        } else {
            clearFieldError('task-due-date', 'due-date-error');
        }
    });

    document.getElementById('filter-status').addEventListener('change', loadTasks);
    document.getElementById('filter-priority').addEventListener('change', loadTasks);
    document.getElementById('sort-by').addEventListener('change', loadTasks);

    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function() {
            loadTasks();
        }, 300);
    });

    document.getElementById('task-form').addEventListener('submit', handleFormSubmit);
});

function showLoading() {
    document.getElementById('task-list').innerHTML = '<tr><td colspan="6" class="text-center">Loading tasks...</td></tr>';
}

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/dashboard`);
        const stats = await response.json();

        console.log('Dashboard stats:', stats);

        const totalEl = document.getElementById('stat-total');
        const pendingEl = document.getElementById('stat-pending');
        const doneEl = document.getElementById('stat-done');
        const overdueEl = document.getElementById('stat-overdue');

        if (totalEl) totalEl.textContent = stats.total;
        if (pendingEl) pendingEl.textContent = stats.pending;
        if (doneEl) doneEl.textContent = stats.done;
        if (overdueEl) overdueEl.textContent = stats.overdue;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadTasks() {
    showLoading();

    const status = document.getElementById('filter-status')?.value || 'all';
    const priority = document.getElementById('filter-priority')?.value || 'all';
    const sort = document.getElementById('sort-by')?.value || '';
    const search = document.getElementById('search-input')?.value || '';

    let url = `${API_BASE}/tasks?`;
    if (status !== 'all') url += `status=${status}&`;
    if (priority !== 'all') url += `priority=${priority}&`;
    if (sort) url += `sort=${sort}&`;
    if (search) url += `search=${encodeURIComponent(search)}&`;

    console.log('Fetching from:', url);

    try {
        const response = await fetch(url);
        console.log('Response status:', response.status);
        const tasks = await response.json();
        console.log('Tasks received:', tasks);

        renderTasks(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
        document.getElementById('task-list').innerHTML =
            '<tr><td colspan="6" class="text-center text-danger">Error loading tasks: ' + error.message + '</td></tr>';
    }
}

function renderTasks(tasks) {
    const tbody = document.getElementById('task-list');

    if (tasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No tasks found</td></tr>';
        return;
    }

    const today = new Date().toISOString().split('T')[0];

    tbody.innerHTML = tasks.map(task => {
        const isOverdue = task.due_date < today && task.status !== 'Done';
        const dueDateClass = isOverdue ? 'overdue' : '';

        return `
            <tr>
                <td><strong>${escapeHtml(task.title)}</strong></td>
                <td>${escapeHtml(task.description || '-')}</td>
                <td class="${dueDateClass}">${formatDate(task.due_date)}</td>
                <td><span class="priority-badge priority-${task.priority.toLowerCase()}">${task.priority}</span></td>
                <td>
                    <select class="form-select form-select-sm status-select"
                            style="width: auto; display: inline-block;"
                            onchange="toggleStatus(${task.id}, this.value)">
                        <option value="Pending" ${task.status === 'Pending' ? 'selected' : ''}>Pending</option>
                        <option value="In Progress" ${task.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Done" ${task.status === 'Done' ? 'selected' : ''}>Done</option>
                    </select>
                </td>
                <td>
                    <button class="btn btn-sm btn-info btn-action" onclick="editTask(${task.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger btn-action" onclick="showDeleteModal(${task.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function openAddModal() {
    isEditing = false;
    document.getElementById('taskModalLabel').textContent = 'Add Task';
    document.getElementById('save-btn').textContent = 'Save';
    document.getElementById('task-id').value = '';
    document.getElementById('task-form').reset();

    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('task-due-date');
    dateInput.setAttribute('min', today);
    dateInput.value = '';
    document.getElementById('task-priority').value = '';
    document.getElementById('date-hint').textContent = 'Select a future date';
    document.getElementById('date-hint').className = 'text-muted';

    clearValidationErrors();
}

async function editTask(taskId) {
    isEditing = true;
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        const task = await response.json();

        document.getElementById('taskModalLabel').textContent = 'Edit Task';
        document.getElementById('save-btn').textContent = 'Update';
        document.getElementById('task-id').value = task.id;
        document.getElementById('task-title').value = task.title;
        document.getElementById('task-description').value = task.description || '';
        document.getElementById('task-due-date').value = task.due_date;

        const today = new Date().toISOString().split('T')[0];
        document.getElementById('task-due-date').setAttribute('min', today);

        document.getElementById('task-status').value = task.status;
        document.getElementById('task-priority').value = task.priority;
        document.getElementById('date-hint').textContent = 'Select a future date';
        document.getElementById('date-hint').className = 'text-muted';

        clearValidationErrors();

        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading task:', error);
        alert('Error loading task details');
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const taskId = document.getElementById('task-id').value;
    const data = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value,
        due_date: document.getElementById('task-due-date').value,
        status: document.getElementById('task-status').value,
        priority: document.getElementById('task-priority').value
    };

    if (!validateForm(data)) {
        return;
    }

    try {
        let url = `${API_BASE}/tasks`;
        let method = 'POST';

        if (taskId) {
            url = `${API_BASE}/tasks/${taskId}`;
            method = 'PUT';
        }

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            if (result.errors) {
                showBackendErrors(result.errors);
            } else {
                alert(result.error || 'Error saving task');
            }
            return;
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
        modal.hide();

        loadTasks();
        loadDashboard();

    } catch (error) {
        console.error('Error saving task:', error);
        alert('Error saving task');
    }
}

function validateForm(data) {
    clearValidationErrors();
    let isValid = true;

    if (!data.title.trim()) {
        showFieldError('task-title', 'title-error', 'Title is required');
        isValid = false;
    } else if (data.title.length > 100) {
        showFieldError('task-title', 'title-error', 'Title must be 100 characters or less');
        isValid = false;
    } else if (data.title.trim().length < 3) {
        showFieldError('task-title', 'title-error', 'Title must be at least 3 characters');
        isValid = false;
    }

    if (data.description && data.description.length > 500) {
        showFieldError('task-description', 'desc-error', 'Description must be 500 characters or less');
        isValid = false;
    }

    if (!data.due_date) {
        showFieldError('task-due-date', 'due-date-error', 'Due date is required');
        isValid = false;
    } else if (!isValidDate(data.due_date)) {
        showFieldError('task-due-date', 'due-date-error', 'Invalid date format');
        isValid = false;
    } else {
        const today = new Date().toISOString().split('T')[0];
        if (data.due_date < today) {
            showFieldError('task-due-date', 'due-date-error', 'Due date cannot be in the past');
            isValid = false;
        }
    }

    const validStatuses = ['Pending', 'In Progress', 'Done'];
    if (!data.status || !validStatuses.includes(data.status)) {
        showFieldError('task-status', 'status-error', 'Please select a valid status');
        isValid = false;
    }

    const validPriorities = ['Low', 'Medium', 'High'];
    if (!data.priority || !validPriorities.includes(data.priority)) {
        showFieldError('task-priority', 'priority-error', 'Please select a priority');
        isValid = false;
    }

    return isValid;
}

function isValidDate(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;

    const date = new Date(dateString);
    return !isNaN(date.getTime());
}

function showFieldError(inputId, errorId, message) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    input.classList.add('is-invalid');
    error.textContent = message;
}

function clearFieldError(inputId, errorId) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    input.classList.remove('is-invalid');
    error.textContent = '';
}

function clearValidationErrors() {
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
}

function showBackendErrors(errors) {
    errors.forEach(error => {
        if (error.toLowerCase().includes('title')) {
            showFieldError('task-title', 'title-error', error);
        } else if (error.toLowerCase().includes('description')) {
            showFieldError('task-description', 'desc-error', error);
        } else if (error.toLowerCase().includes('due')) {
            showFieldError('task-due-date', 'due-date-error', error);
        }
    });
}

async function toggleStatus(taskId, newStatus) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            const result = await response.json();
            alert(result.errors ? result.errors.join(', ') : 'Error updating status');
            loadTasks();
            return;
        }

        loadTasks();
        loadDashboard();
    } catch (error) {
        console.error('Error updating status:', error);
        alert('Error updating status');
        loadTasks();
    }
}

function showDeleteModal(taskId) {
    document.getElementById('delete-task-id').value = taskId;
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

async function confirmDelete() {
    const taskId = document.getElementById('delete-task-id').value;

    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const result = await response.json();
            alert(result.error || 'Error deleting task');
            return;
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
        modal.hide();

        loadTasks();
        loadDashboard();
    } catch (error) {
        console.error('Error deleting task:', error);
        alert('Error deleting task');
    }
}
