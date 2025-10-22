document.addEventListener('DOMContentLoaded', function () {
    const statusElement = document.getElementById('status');

    fetch('http://127.0.0.1:5000/status')
        .then(response => {
            if (response.ok) {
                statusElement.textContent = 'Active';
                statusElement.classList.add('active');
            } else {
                throw new Error('Server offline');
            }
        })
        .catch(error => {
            statusElement.textContent = 'Offline';
            statusElement.classList.add('offline');
        });
});
