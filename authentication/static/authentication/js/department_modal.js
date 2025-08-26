
// Helper to capitalize names
function capitalizeName(fullName) {
    if (!fullName) return '';
    return fullName.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
}

// Make functions global
window.openModal = function(departmentId, departmentName) {
    const modal = document.getElementById("removeModal");
    const form = document.getElementById("removeForm");
    const message = document.getElementById("modalMessage");

    form.action = `/department/remove/${departmentId}/`;
    message.textContent = `Are you sure you want to remove the department "${departmentName}"?`;
    modal.classList.remove("hidden");
};

window.closeModal = function() {
    document.getElementById("removeModal").classList.add("hidden");
};

window.openInfoModal = function(departmentId, title, description, managerName, managerLink) {
    const infoTitle = document.getElementById('infoTitle');
    const infoDescription = document.getElementById('infoDescription');
    const infoManager = document.getElementById('infoManager');
    const employeesList = document.getElementById('infoEmployees');

    infoTitle.textContent = title;
    infoDescription.textContent = description;

    // Manager
    infoManager.innerHTML = '';
    if (managerName && managerName !== 'Not Assigned') {
        const a = document.createElement('a');
        a.href = managerLink || '#';
        a.textContent = capitalizeName(managerName);
        a.classList.add('hover:underline','text-gray-400');
        infoManager.appendChild(a);
    } else {
        infoManager.textContent = 'Not Assigned';
        infoManager.classList.add('text-gray-400');
    }

    // Employees - Fetch dynamically
    employeesList.innerHTML = '<li>Loading employees...</li>'; // Loading state
    fetch(`/department/${departmentId}/employees/`)
        .then(response => response.json())
        .then(data => {
            debugger;
            const employees = data.employees;
            employeesList.innerHTML = ''; // Clear loading state
            if (data && data.length) {
                data.forEach(emp => {
                    const li = document.createElement('li'); //bullet
                    li.classList.add('list-disc', 'marker:text-white', 'ml-4');
                    if (emp.name) {
                        const a = document.createElement('a'); //clickable
                        a.href = emp.link || '#';
                        a.textContent = capitalizeName(emp.name);
                        a.classList.add('hover:underline','text-gray-400');
                        li.appendChild(a);
                    } else {
                        li.textContent = 'Unknown';
                    }
                    employeesList.appendChild(li);
                });
            } else {
                employeesList.textContent = 'No employees assigned.';
            }
        })
        .catch(error => {
            // console.error('Error fetching employees:', error);
            employeesList.textContent = 'Failed to load employees.';
        });

    document.getElementById('infoModal').classList.remove('hidden');
};

window.closeInfoModal = function() {
    document.getElementById('infoModal').classList.add('hidden');
};
