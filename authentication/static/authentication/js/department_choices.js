document.addEventListener('DOMContentLoaded', function () {
    const el = document.querySelector('#id_employees');
    if (el) {
        new Choices(el, {
            removeItemButton: true,
            placeholderValue: 'Select employees',
            searchPlaceholderValue: 'Search employees',
            shouldSort: false
        });
    }
});
