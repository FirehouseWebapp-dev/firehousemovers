document.addEventListener('DOMContentLoaded', function () {
    // Employees multi-select
    new Choices('#id_employees', {
        removeItemButton: true,
        placeholderValue: 'Select employees',
        searchPlaceholderValue: 'Search employees',
        shouldSort: false
    });
});
