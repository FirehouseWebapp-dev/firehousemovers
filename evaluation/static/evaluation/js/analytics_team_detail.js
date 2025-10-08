// Analytics Team Detail - JavaScript
// Handles team member performance trends viewing

/**
 * View employee performance trends
 * @param {number} employeeId - The ID of the employee to view trends for
 */
function viewEmployeeTrend(employeeId) {
    window.location.href = `/evaluation/employee-dashboard/?employee_id=${employeeId}`;
}

