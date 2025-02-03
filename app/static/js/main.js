document.addEventListener('DOMContentLoaded', function() {
    // Initialize Database Button
    const initDbButton = document.getElementById('initDbButton');
    const initDbStatus = document.getElementById('initDbStatus');

    initDbButton.addEventListener('click', function() {
        initDbButton.disabled = true;
        initDbStatus.innerHTML = '<div class="text-info">Initializing database...</div>';

        fetch('/initdb')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    initDbStatus.innerHTML = `<div class="text-danger">Error: ${data.error}</div>`;
                } else {
                    initDbStatus.innerHTML = '<div class="text-success">Database initialized successfully!</div>';
                    // Reload all data
                    loadTableData('customers');
                    loadTableData('orders');
                    loadTableData('products');
                    loadTableData('orderItems');
                    loadAssignmentData(1);
                    loadAssignmentData(2);
                    loadAssignmentData(3);
                    loadAssignmentData(4);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                initDbStatus.innerHTML = '<div class="text-danger">Error initializing database</div>';
            })
            .finally(() => {
                initDbButton.disabled = false;
            });
    });

    // Load all tables
    loadTableData('customers');
    loadTableData('orders');
    loadTableData('products');
    loadTableData('orderItems');

    // Load assignment results
    loadAssignmentData(1);
    loadAssignmentData(2);
    loadAssignmentData(3);
    loadAssignmentData(4);
});

function loadTableData(tableName) {
    const tableBody = document.querySelector(`#${tableName}Table tbody`);
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';

    fetch(`/table/${tableName}`)
        .then(response => response.json())
        .then(data => {
            tableBody.innerHTML = '';
            data.data.forEach(row => {
                const tr = document.createElement('tr');
                Object.values(row).forEach(value => {
                    const td = document.createElement('td');
                    td.textContent = value;
                    tr.appendChild(td);
                });
                tableBody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading data</td></tr>';
        });
}

function loadAssignmentData(assignmentNumber) {
    const resultDiv = document.querySelector(`#assignment${assignmentNumber}Results`);
    resultDiv.classList.add('loading');

    fetch(`/assignment${assignmentNumber}`)
        .then(response => response.json())
        .then(data => {
            resultDiv.classList.remove('loading');
            
            // Create table
            const table = document.createElement('table');
            table.className = 'table table-striped';
            
            // Create header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            if (data.data && data.data.length > 0) {
                Object.keys(data.data[0]).forEach(key => {
                    const th = document.createElement('th');
                    th.textContent = key.replace(/_/g, ' ').toUpperCase();
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);
            }
            
            // Create body
            const tbody = document.createElement('tbody');
            data.data.forEach(row => {
                const tr = document.createElement('tr');
                Object.values(row).forEach(value => {
                    const td = document.createElement('td');
                    td.textContent = value;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            
            resultDiv.innerHTML = '';
            resultDiv.appendChild(table);
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.classList.remove('loading');
            resultDiv.innerHTML = '<div class="alert alert-danger">Error loading data</div>';
        });
} 