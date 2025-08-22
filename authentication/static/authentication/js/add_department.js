document.addEventListener('DOMContentLoaded', function () {
    // Employees multi-select
    new Choices('#id_roles', {
        removeItemButton: true,
        placeholderValue: 'Select employees',
        searchPlaceholderValue: 'Search employees',
        shouldSort: false
    });
});

  