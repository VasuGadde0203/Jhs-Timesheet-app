let rowCount = 0;
let sectionCount = 0;
let employeeData = [];
let clientData = [];
let currentRow = null;
let weekOptions = [];
let loggedInEmployeeId = localStorage.getItem('loggedInEmployeeId');
let copiedData = null; // Store copied row data
const API_URL = '';

const getHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
});

document.addEventListener('DOMContentLoaded', async function() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login'; // Consistent redirect path
        return;
    }

    // Verify session   
    try {
        const response = await fetch('/verify_session', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('loggedInEmployeeId');
            window.location.href = '/login';
            return;
        }
    } catch (error) {
        console.error('Session verification failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('loggedInEmployeeId');
        window.location.href = '/login';
        return;
    }

    // Show loading indicator for employee data fetch
    showLoading("Fetching Employee Data");

    // Initialize data
    if (loggedInEmployeeId) {
        try {
            employeeData = await fetchData('/employees');
            clientData = await fetchData('/clients');
            computeWeekOptions();
            await populateEmployeeInfo();
            addWeekSection();
            showSection('timesheet');
        } catch (error) {
            console.error('Error initializing data:', error);
            showError('Failed to load employee data. Please try again.');
        } finally {
            hideLoading();
        }
    }
});

async function checkSession() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/static/login.html';
        return;
    }
    try {
        const response = await fetch(`${API_URL}/verify_session`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('loggedInEmployeeId');
            window.location.href = '/static/login.html';
        }
    } catch (error) {
        console.error('Session check failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('loggedInEmployeeId');
        window.location.href = '/static/login.html';
    }
}

async function fetchData(endpoint) {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/static/login.html';
            return [];
        }
        const response = await fetch(`${API_URL}${endpoint}`, {
            headers: getHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('loggedInEmployeeId');
                window.location.href = '/static/login.html';
            }
            throw new Error(`Failed to fetch ${endpoint}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        showError(`Error fetching ${endpoint.split('/')[1]} data. Please try again.`);
        return [];
    }
}

function computeWeekOptions() {
    const today = new Date(2025, 8, 8);
    const payroll = getPayrollPeriod(today);
    weekOptions = generateWeekOptions(payroll.start, payroll.end);
}

function getPayrollPeriod(today) {
    let start = new Date(2025, 7, 21);
    let end = new Date(2025, 8, 20);
    return { start, end };
}

function generateWeekOptions(start, end) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    let weeks = [];
    let current = new Date(start);
    let weekNum = 1;
    while (current <= end) {
        let weekStart = new Date(current);
        let daysToSunday = (7 - weekStart.getDay()) % 7;
        let weekEnd = new Date(weekStart);
        weekEnd.setDate(weekEnd.getDate() + daysToSunday);
        if (weekEnd > end) {
            weekEnd = new Date(end);
        }
        let wsDay = weekStart.getDate().toString().padStart(2, '0');
        let wsMonth = months[weekStart.getMonth()];
        let weDay = weekEnd.getDate().toString().padStart(2, '0');
        let weMonth = months[weekEnd.getMonth()];
        let value = `${wsDay}/${weekStart.getMonth() + 1}/${weekStart.getFullYear()} to ${weDay}/${weekEnd.getMonth() + 1}/${weekEnd.getFullYear()}`;
        let text = `Week ${weekNum} (${wsDay} ${wsMonth} - ${weDay} ${weMonth})`;
        weeks.push({ value, text, start: weekStart, end: weekEnd });
        current = new Date(weekEnd);
        current.setDate(current.getDate() + 1);
        weekNum++;
    }
    return weeks;
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showPopup(message, isError = false) {
    const popup = document.getElementById('successPopup');
    const popupMessage = document.getElementById('popupMessage');
    popupMessage.textContent = message;
    popup.className = 'popup' + (isError ? ' error' : '');
    popup.style.display = 'block';
    setTimeout(closePopup, 3000);
}

function closePopup() {
    document.getElementById('successPopup').style.display = 'none';
}


function showLoading(text = "Saving...") {
    const loadingBar = document.getElementById('loadingBar');
    if (loadingBar) {
        loadingBar.textContent = `${text}...`;
        loadingBar.style.display = 'block';
    }
}

function hideLoading() {
    const loadingBar = document.getElementById('loadingBar');
    if (loadingBar) {
        loadingBar.style.display = 'none';
    }
}

function fetchEmployeeData(empId) {
    const cleanEmpId = empId.trim();
    const employee = employeeData.find(e => e['EmpID']?.toString().trim() === cleanEmpId);
    if (!employee) {
        showError(`No employee found for ID: ${empId}`);
        return null;
    }
    return { ...employee };
}

async function populateEmployeeInfo() {
    const employee = fetchEmployeeData(loggedInEmployeeId);
    if (employee) {
        const fields = {
            employeeId: employee['EmpID'] || '',
            employeeName: employee['Emp Name'] || '',
            designation: employee['Designation Name'] || '',
            partner: employee['Partner'] || '',
            reportingManager: employee['ReportingEmpName'] || '',
            gender: employee['Gender'] === 'F' ? 'Female' : employee['Gender'] === 'M' ? 'Male' : ''
        };
        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.value = value;
        });
        updateAllClientFields();
        updateAllReportingManagerFields();
    }
}

function fetchProjectData(tl, manager) {
    const cleanTL = tl ? tl.trim().toLowerCase() : '';
    const cleanManager = manager ? manager.trim().toLowerCase() : '';
    let projects = clientData.filter(p => 
        p['TLs/Manager']?.toString().trim().toLowerCase() === cleanTL || 
        p['TLs/Manager']?.toString().trim().toLowerCase() === cleanManager
    );
    projects = projects.map(p => {
        const cleaned = { ...p };
        cleaned['CLIENT NAME'] = cleanClientName(p['CLIENT NAME']);
        return cleaned;
    });
    const uniqueProjects = [];
    const seen = new Set();
    projects.forEach(p => {
        const key = `${p['PROJECT ID']}|${p['CLIENT NAME']}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueProjects.push(p);
        }
    });
    return uniqueProjects;
}

function cleanClientName(name) {
    if (!name) return "";
    name = name.replace(/_x000D_|\n|\r/g, '');
    return name.trim().replace(/\s+/g, ' ');
}

function getReportingManagers() {
    const managers = [...new Set(employeeData
        .map(e => e['ReportingEmpName'])
        .filter(m => m && typeof m === 'string' && m.trim()))];
    return managers;
}

let customClients = new Set(); // Global set to track unique custom clients

// function updateAllClientFields() {
//     const sections = document.querySelectorAll('.timesheet-section, .history-table');
//     const tl = document.getElementById('partner')?.value || '';
//     const manager = document.getElementById('reportingManager')?.value || '';
//     const relevantProjects = fetchProjectData(tl, manager);
    
//     sections.forEach(section => {
//         const clientFields = section.querySelectorAll('.client-field');
//         clientFields.forEach(field => {
//             const row = field.closest('tr');
//             const projectCodeInput = row.querySelector('.project-code');
//             const currentClientValue = field.value || field.querySelector('option:checked')?.value || '';
            
//             if (relevantProjects.length > 0) {
//                 const select = document.createElement('select');
//                 select.className = 'client-field client-select';
//                 select.innerHTML = '<option value="">Select Client</option>';
//                 relevantProjects.forEach(project => {
//                     const option = document.createElement('option');
//                     option.value = project['CLIENT NAME'];
//                     option.textContent = project['CLIENT NAME'];
//                     select.appendChild(option);
//                 });
//                 select.innerHTML += '<option value="Type here">Type here</option>';
//                 select.dataset.projects = JSON.stringify(relevantProjects);
//                 select.onchange = () => handleClientChange(select);
//                 if (currentClientValue && (relevantProjects.some(p => p['CLIENT NAME'] === currentClientValue) || currentClientValue === 'Type here')) {
//                     select.value = currentClientValue;
//                 }
//                 field.replaceWith(select);
//                 projectCodeInput.readOnly = select.value !== 'Type here';
//                 updateProjectCode(select);
//             } else {
//                 const input = document.createElement('input');
//                 input.type = 'text';
//                 input.className = 'client-field client-input';
//                 input.placeholder = 'Enter Client';
//                 input.value = currentClientValue;
//                 input.oninput = () => {
//                     projectCodeInput.readOnly = false;
//                     projectCodeInput.placeholder = 'Enter Project Code';
//                     updateSummary();
//                 };
//                 field.replaceWith(input);
//                 projectCodeInput.readOnly = false;
//                 projectCodeInput.placeholder = 'Enter Project Code';
//                 projectCodeInput.oninput = updateSummary;
//             }
//         });
//     });
//     updateModalClientFields();
// }

function updateAllClientFields() {
    const sections = document.querySelectorAll('.timesheet-section, .history-table');
    const tl = document.getElementById('partner')?.value || '';
    const manager = document.getElementById('reportingManager')?.value || '';
    const relevantProjects = fetchProjectData(tl, manager);

    // Collect custom clients
    customClients.clear();
    sections.forEach(section => {
        const clientFields = section.querySelectorAll('.client-field');
        clientFields.forEach(field => {
            const value = field.value || field.querySelector('option:checked')?.value || '';
            if (value && value !== 'Type here' && !relevantProjects.some(p => p['CLIENT NAME'] === value)) {
                customClients.add(value);
            }
        });
    });

    // Update fields, skip inputs
    sections.forEach(section => {
        const clientFields = section.querySelectorAll('.client-field');
        clientFields.forEach(field => {
            if (field.tagName === 'INPUT') {
                const row = field.closest('tr');
                const projectCodeInput = row.querySelector('.project-code');
                projectCodeInput.readOnly = false;
                projectCodeInput.placeholder = 'Enter Project Code';
                return;
            }

            const row = field.closest('tr');
            const projectCodeInput = row.querySelector('.project-code');
            const currentClientValue = field.value || field.querySelector('option:checked')?.value || '';

            const select = document.createElement('select');
            select.className = 'client-field client-select';
            select.innerHTML = '<option value="">Select Client</option>';
            relevantProjects.forEach(project => {
                const option = document.createElement('option');
                option.value = project['CLIENT NAME'];
                option.textContent = project['CLIENT NAME'];
                select.appendChild(option);
            });
            customClients.forEach(custom => {
                const option = document.createElement('option');
                option.value = custom;
                option.textContent = custom;
                select.appendChild(option);
            });
            select.innerHTML += '<option value="Type here">Type here</option>';
            select.dataset.projects = JSON.stringify(relevantProjects);
            select.onchange = () => handleClientChange(select);
            if (currentClientValue && (relevantProjects.some(p => p['CLIENT NAME'] === currentClientValue) || customClients.has(currentClientValue) || currentClientValue === 'Type here')) {
                select.value = currentClientValue;
            }
            field.replaceWith(select);
            projectCodeInput.readOnly = select.value !== 'Type here' && relevantProjects.some(p => p['CLIENT NAME'] === select.value);
            updateProjectCode(select);
        });
    });
    updateModalClientFields();
}

function handleClientChange(select) {
    if (!select) return;
    const row = select.closest('tr');
    const projectCodeInput = row.querySelector('.project-code');
    if (select.value === 'Type here') {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'client-field client-input';
        input.placeholder = 'Enter Client';
        input.oninput = () => {
            projectCodeInput.readOnly = false;
            projectCodeInput.placeholder = 'Enter Project Code';
            updateSummary();
        };
        select.replaceWith(input);
        projectCodeInput.readOnly = false;
        projectCodeInput.placeholder = 'Enter Project Code';
        projectCodeInput.oninput = updateSummary;
    } else {
        updateProjectCode(select);
    }
}

// function updateProjectCode(clientSelect) {
//     if (!clientSelect) return;
//     const row = clientSelect.closest('tr');
//     const projectCodeInput = row.querySelector('.project-code');
//     const selectedClient = clientSelect.value;
    
//     if (selectedClient === 'Type here') {
//         projectCodeInput.readOnly = false;
//         projectCodeInput.placeholder = 'Enter Project Code';
//         projectCodeInput.value = '';
//         projectCodeInput.oninput = updateSummary;
//     } else {
//         const projects = JSON.parse(clientSelect.dataset.projects || '[]');
//         const project = projects.find(p => p['CLIENT NAME'] === selectedClient);
//         projectCodeInput.value = project ? project['PROJECT ID'] : '';
//         projectCodeInput.readOnly = true;
//         updateSummary();
//     }
// }

function updateProjectCode(clientSelect) {
    if (!clientSelect) return;
    const row = clientSelect.closest('tr');
    const projectCodeInput = row.querySelector('.project-code');
    const selectedClient = clientSelect.value;

    if (selectedClient === 'Type here') {
        projectCodeInput.readOnly = false;
        projectCodeInput.placeholder = 'Enter Project Code';
        projectCodeInput.value = '';
        projectCodeInput.oninput = updateSummary;
    } else {
        const projects = JSON.parse(clientSelect.dataset.projects || '[]');
        const project = projects.find(p => p['CLIENT NAME'] === selectedClient);
        if (project) {
            projectCodeInput.value = project['PROJECT ID'];
            projectCodeInput.readOnly = true;
        } else {
            // For custom clients
            projectCodeInput.readOnly = false;
            projectCodeInput.placeholder = 'Enter Project Code';
            // Preserve existing value
        }
        updateSummary();
    }
}

function saveModalEntry() {
    if (!currentRow) return;
    const modalInputs = document.querySelectorAll('#modalOverlay input, #modalOverlay select');
    const rowInputs = currentRow.querySelectorAll('input, select');

    // Copy modal inputs to row inputs
    for (let i = 0; i < modalInputs.length; i++) {
        if (rowInputs[i].tagName === 'INPUT' && rowInputs[i].type !== 'button') {
            rowInputs[i].value = modalInputs[i].value;
        } else if (rowInputs[i].tagName === 'SELECT') {
            rowInputs[i].value = modalInputs[i].value;
        }
    }

    // Handle custom client input from "Type here"
    const modalClientField = modalInputs[6]; // Client field in modal
    const rowClientField = rowInputs[6]; // Client field in row
    const modalProjectCodeField = modalInputs[8]; // Project code in modal
    const rowProjectCodeField = rowInputs[8]; // Project code in row

    // If modal client field is an input (from "Type here"), ensure row client field is also an input
    if (modalClientField.tagName === 'INPUT' && modalClientField.value && modalClientField.value !== 'Type here') {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'client-field client-input form-input';
        input.value = modalClientField.value;
        input.placeholder = 'Enter Client';
        input.oninput = () => {
            rowProjectCodeField.readOnly = false;
            rowProjectCodeField.placeholder = 'Enter Project Code';
            updateSummary();
        };
        rowClientField.replaceWith(input);

        // Ensure project code field is editable and preserves the value
        rowProjectCodeField.readOnly = false;
        rowProjectCodeField.value = modalProjectCodeField.value;
        rowProjectCodeField.placeholder = 'Enter Project Code';
        rowProjectCodeField.oninput = updateSummary;

        // Add custom client to customClients set for future dropdowns
        if (modalClientField.value) {
            customClients.add(modalClientField.value);
        }
    } else if (modalClientField.value && modalClientField.value !== 'Type here') {
        // If a predefined client is selected, ensure project code is updated
        updateProjectCode(rowClientField);
    }

    calculateHours(currentRow);
    validateDate(currentRow.querySelector('.date-field'));
    closeModal();
    updateSummary();
    updateAllClientFields(); // Refresh dropdowns to include new custom client
}

function updateAllReportingManagerFields() {
    const sections = document.querySelectorAll('.timesheet-section, .history-table');
    const managers = getReportingManagers();
    const empReportingManager = document.getElementById('reportingManager')?.value || '';
    
    sections.forEach(section => {
        const reportingFields = section.querySelectorAll('.reporting-manager-field');
        reportingFields.forEach(field => {
            const currentValue = field.value || field.querySelector('option:checked')?.value || '';
            
            const select = document.createElement('select');
            select.className = 'reporting-manager-field reporting-manager-select';
            select.innerHTML = '<option value="">Select Reporting Manager</option>';
            if (empReportingManager) {
                const option = document.createElement('option');
                option.value = empReportingManager;
                option.textContent = empReportingManager;
                select.appendChild(option);
            }
            managers.forEach(manager => {
                if (manager !== empReportingManager) {
                    const option = document.createElement('option');
                    option.value = manager;
                    option.textContent = manager;
                    select.appendChild(option);
                }
            });
            select.innerHTML += '<option value="Type here">Type here</option>';
            select.onchange = () => handleReportingManagerChange(select);
            if (currentValue && (managers.includes(currentValue) || currentValue === empReportingManager || currentValue === 'Type here')) {
                select.value = currentValue;
            }
            field.replaceWith(select);
            if (select.value === 'Type here') {
                handleReportingManagerChange(select);
            }
        });
    });
    updateModalReportingManagerFields();
}

function handleReportingManagerChange(select) {
    if (!select) return;
    if (select.value === 'Type here') {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'reporting-manager-field reporting-manager-input';
        input.placeholder = 'Enter Reporting Manager';
        input.oninput = updateSummary;
        select.replaceWith(input);
    } else {
        updateSummary();
    }
}

function calculateHours(row) {
    if (!row) return;
    const isValid = validateTimes(row);
    if (!isValid) {
        const projectHoursField = row.querySelector('.project-hours-field');
        const workingHoursField = row.querySelector('.working-hours-field');
        if (projectHoursField) projectHoursField.value = '';
        if (workingHoursField) workingHoursField.value = '';
        return;
    }

    const projectStart = row.querySelector('.project-start')?.value;
    const projectEnd = row.querySelector('.project-end')?.value;
    const punchIn = row.querySelector('.punch-in')?.value;
    const punchOut = row.querySelector('.punch-out')?.value;

    let projectHours = 0;
    if (projectStart && projectEnd) {
        const [startH, startM] = projectStart.split(':').map(Number);
        const [endH, endM] = projectEnd.split(':').map(Number);
        const startMinutes = startH * 60 + startM;
        const endMinutes = endH * 60 + endM;
        projectHours = (endMinutes - startMinutes) / 60;
        if (projectHours < 0) projectHours += 24;
        projectHours = Math.max(0, projectHours).toFixed(2);
    }

    let workingHours = 0;
    if (punchIn && punchOut) {
        const [inH, inM] = punchIn.split(':').map(Number);
        const [outH, outM] = punchOut.split(':').map(Number);
        const inMinutes = inH * 60 + inM;
        const outMinutes = outH * 60 + outM;
        workingHours = (outMinutes - inMinutes) / 60;
        if (workingHours < 0) workingHours += 24;
        workingHours = Math.max(0, workingHours).toFixed(2);
    }

    const projectHoursField = row.querySelector('.project-hours-field');
    const workingHoursField = row.querySelector('.working-hours-field');
    if (projectHoursField) {
        projectHoursField.value = projectHours > 0 ? projectHours : '';
    }
    if (workingHoursField) {
        workingHoursField.value = workingHours > 0 ? workingHours : '';
    }
    updateSummary();
}


function updateExistingRowDates(sectionId) {
    const tbody = document.getElementById(`timesheetBody_${sectionId.split('_')[1]}`);
    if (!tbody) return;
    
    const weekSelect = document.getElementById(`weekPeriod_${sectionId.split('_')[1]}`);
    const selectedWeekValue = weekSelect.value;
    const selectedWeek = weekOptions.find(opt => opt.value === selectedWeekValue);
    
    if (selectedWeek && selectedWeek.start) {
        const weekStart = new Date(selectedWeek.start);
        const defaultDate = `${weekStart.getFullYear()}-${String(weekStart.getMonth() + 1).padStart(2, '0')}-${String(weekStart.getDate()).padStart(2, '0')}`;
        
        const dateInputs = tbody.querySelectorAll('.date-field');
        dateInputs.forEach(dateInput => {
            const currentDate = new Date(dateInput.value + 'T00:00:00');
            const weekStartDate = new Date(weekStart);
            const weekEndDate = new Date(selectedWeek.end);
            
            if (!dateInput.value || currentDate < weekStartDate || currentDate > weekEndDate) {
                dateInput.value = defaultDate;
                validateDate(dateInput);
            }
        });
    }
}

function validateHours(hoursInput) {
    if (!hoursInput) return;
    const hours = parseFloat(hoursInput.value);
    if (hours > 16) {
        hoursInput.classList.add('validation-error');
        showValidationMessage(hoursInput, 'Hours cannot exceed 16 per day');
    } else {
        hoursInput.classList.remove('validation-error');
        clearValidationMessage(hoursInput);
    }
}

function validateDate(dateInput) {
    if (!dateInput) return;
    const section = dateInput.closest('.timesheet-section');
    const weekSelect = section.querySelector('.week-period select');
    const selectedWeek = weekOptions.find(opt => opt.value === weekSelect.value);
    if (!selectedWeek) return;

    const inputDate = new Date(dateInput.value);
    const weekStart = new Date(selectedWeek.start);
    const weekEnd = new Date(selectedWeek.end);

    if (inputDate < weekStart || inputDate > weekEnd) {
        dateInput.classList.add('validation-error');
        showValidationMessage(dateInput, 'Please select a date within the specified week only.');
    } else {
        dateInput.classList.remove('validation-error');
        clearValidationMessage(dateInput);
    }

    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (60 * 24 * 60 * 60 * 1000));
    const sevenDaysAhead = new Date(today.getTime() + (7 * 24 * 60 * 60 * 1000));
    
    if (inputDate < thirtyDaysAgo || inputDate > sevenDaysAhead) {
        dateInput.classList.add('validation-error');
        showValidationMessage(dateInput, 'Date must be within last 30 days to next 7 days');
    }
}

function validateModalDate(dateInput) {
    if (!dateInput || !currentRow) return;
    const section = currentRow.closest('.timesheet-section');
    const weekSelect = section.querySelector('.week-period select');
    const selectedWeek = weekOptions.find(opt => opt.value === weekSelect.value);
    if (!selectedWeek) return;

    const inputDate = new Date(dateInput.value);
    const weekStart = new Date(selectedWeek.start);
    const weekEnd = new Date(selectedWeek.end);

    if (inputDate < weekStart || inputDate > weekEnd) {
        dateInput.classList.add('validation-error');
        showValidationMessage(dateInput, 'Please select a date within the specified week only.');
    } else {
        dateInput.classList.remove('validation-error');
        clearValidationMessage(dateInput);
    }

    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (60 * 24 * 60 * 60 * 1000));
    const sevenDaysAhead = new Date(today.getTime() + (7 * 24 * 60 * 60 * 1000));
    
    if (inputDate < thirtyDaysAgo || inputDate > sevenDaysAhead) {
        dateInput.classList.add('validation-error');
        showValidationMessage(dateInput, 'Date must be within last 60 days to next 7 days');
    }
}

function showValidationMessage(element, message) {
    if (!element) return;
    clearValidationMessage(element);
    const msgDiv = document.createElement('div');
    msgDiv.className = 'validation-message';
    msgDiv.textContent = message;
    element.parentNode.appendChild(msgDiv);
}

function clearValidationMessage(element) {
    if (!element) return;
    const existingMsg = element.parentNode.querySelector('.validation-message');
    if (existingMsg) existingMsg.remove();
}

function deleteRow(button) {
    const row = button.closest('tr');
    if (row) {
        const tbody = row.closest('tbody');
        row.remove();
        updateRowNumbers(tbody.id);
        updateSummary();
    }
}

function updateRowNumbers(tbodyId) {
    const tbody = document.getElementById(tbodyId);
    const rows = tbody.querySelectorAll('tr');
    rows.forEach((row, index) => {
        row.cells[0].textContent = index + 1;
    });
}

function deleteWeekSection(sectionId) {
    if (confirm('Are you sure you want to delete this week section?')) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.remove();
            updateSummary();
        }
    }
}

function openModal(button) {
    currentRow = button.closest('tr');
    const inputs = currentRow.querySelectorAll('input, select');
    
    const labels = [
        'Date', 'Location of Work', 'Punch In', 'Punch Out', 'Project Start Time', 'Project End Time',
        'Client', 'Project', 'Project Code', 'Reporting Manager', 'Activity', 'Project Hours', 'Working Hours', 'Billable', 'Remarks'
    ];
    
    for (let i = 0; i < inputs.length; i++) {
        const label = document.getElementById(`modalLabel${i + 1}`);
        const input = document.getElementById(`modalInput${i + 1}`);
        if (label && input) {
            label.textContent = labels[i];
            input.value = inputs[i].value || '';
            
            if (input.tagName === 'SELECT') {
                if (i === 6) {
                    const select = inputs[i];
                    const relevantProjects = fetchProjectData(document.getElementById('partner')?.value || '', document.getElementById('reportingManager')?.value || '');
                    input.innerHTML = '<option value="">Select Client</option>';
                    relevantProjects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project['CLIENT NAME'];
                        option.textContent = project['CLIENT NAME'];
                        input.appendChild(option);
                    });
                    input.innerHTML += '<option value="Type here">Type here</option>';
                    input.value = select.value || '';
                } else if (i === 13) {
                    input.value = inputs[i].value || 'Yes';
                }
            }
        }
    }
    document.getElementById('modalOverlay').style.display = 'flex';
    updateModalClientFields();
    updateModalReportingManagerFields();
    validateModalDate(document.getElementById('modalInput1'));
    updateModalHours();
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
    currentRow = null;
}

function updateModalClientFields() {
    const modalClientSelect = document.getElementById('modalInput7');
    const relevantProjects = fetchProjectData(document.getElementById('partner')?.value || '', document.getElementById('reportingManager')?.value || '');
    modalClientSelect.innerHTML = '<option value="">Select Client</option>';
    relevantProjects.forEach(project => {
        const option = document.createElement('option');
        option.value = project['CLIENT NAME'];
        option.textContent = project['CLIENT NAME'];
        modalClientSelect.appendChild(option);
    });
    modalClientSelect.innerHTML += '<option value="Type here">Type here</option>';
    if (currentRow) {
        const clientField = currentRow.querySelector('.client-field');
        modalClientSelect.value = clientField.value || clientField.querySelector('option:checked')?.value || '';
    }
    modalClientSelect.onchange = updateModalProjectCode; // Ensure this is set
}

function updateModalReportingManagerFields() {
    const modalManagerSelect = document.getElementById('modalInput10');
    const managers = getReportingManagers();
    const empReportingManager = document.getElementById('reportingManager')?.value || '';
    modalManagerSelect.innerHTML = '<option value="">Select Reporting Manager</option>';
    if (empReportingManager) {
        const option = document.createElement('option');
        option.value = empReportingManager;
        option.textContent = empReportingManager;
        modalManagerSelect.appendChild(option);
    }
    managers.forEach(manager => {
        if (manager !== empReportingManager) {
            const option = document.createElement('option');
            option.value = manager;
            option.textContent = manager;
            modalManagerSelect.appendChild(option);
        }
    });
    modalManagerSelect.innerHTML += '<option value="Type here">Type here</option>';
    if (currentRow) {
        const managerField = currentRow.querySelector('.reporting-manager-field');
        modalManagerSelect.value = managerField.value || managerField.querySelector('option:checked')?.value || '';
    }
}


function updateModalProjectCode() {
    const modalClientSelect = document.getElementById('modalInput7');
    const modalProjectCodeInput = document.getElementById('modalInput9');
    if (!modalClientSelect || !modalProjectCodeInput) return;

    if (modalClientSelect.value === 'Type here') {
        // Replace dropdown with text input
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'client-field client-input form-input';
        input.placeholder = 'Enter Client';
        input.id = 'modalInput7';
        input.oninput = () => {
            modalProjectCodeInput.readOnly = false;
            modalProjectCodeInput.placeholder = 'Enter Project Code';
            updateModalHours();
        };
        modalClientSelect.replaceWith(input);

        // Make project code field editable
        modalProjectCodeInput.readOnly = false;
        modalProjectCodeInput.placeholder = 'Enter Project Code';
        modalProjectCodeInput.value = '';
        modalProjectCodeInput.oninput = updateModalHours;
    } else {
        // Update project code based on selected client
        const projects = fetchProjectData(
            document.getElementById('partner')?.value || '',
            document.getElementById('reportingManager')?.value || ''
        );
        const project = projects.find(p => p['CLIENT NAME'] === modalClientSelect.value);
        modalProjectCodeInput.value = project ? project['PROJECT ID'] : '';
        modalProjectCodeInput.readOnly = true;
        updateModalHours();
    }
}

function updateModalHours() {
    if (!currentRow) return;
    const projectStart = document.getElementById('modalInput5').value;
    const projectEnd = document.getElementById('modalInput6').value;
    const punchIn = document.getElementById('modalInput3').value;
    const punchOut = document.getElementById('modalInput4').value;

    let projectHours = 0;
    if (projectStart && projectEnd) {
        const [startH, startM] = projectStart.split(':').map(Number);
        const [endH, endM] = projectEnd.split(':').map(Number);
        const startMinutes = startH * 60 + startM;
        const endMinutes = endH * 60 + endM;
        projectHours = (endMinutes - startMinutes) / 60;
        if (projectHours < 0) projectHours += 24;
        projectHours = projectHours.toFixed(2);
    }

    let workingHours = 0;
    if (punchIn && punchOut) {
        const [inH, inM] = punchIn.split(':').map(Number);
        const [outH, outM] = punchOut.split(':').map(Number);
        const inMinutes = inH * 60 + inM;
        const outMinutes = outH * 60 + outM;
        workingHours = (outMinutes - inMinutes) / 60;
        if (workingHours < 0) workingHours += 24;
        workingHours = workingHours.toFixed(2);
    }

    document.getElementById('modalInput12').value = projectHours;
    document.getElementById('modalInput13').value = workingHours;
}

// function saveModalEntry() {
//     if (!currentRow) return;
//     const modalInputs = document.querySelectorAll('#modalOverlay input, #modalOverlay select');
//     const rowInputs = currentRow.querySelectorAll('input, select');
    
//     for (let i = 0; i < modalInputs.length; i++) {
//         if (rowInputs[i].tagName === 'INPUT' && rowInputs[i].type !== 'button') {
//             rowInputs[i].value = modalInputs[i].value;
//         } else if (rowInputs[i].tagName === 'SELECT') {
//             rowInputs[i].value = modalInputs[i].value;
//         }
//     }
//     calculateHours(currentRow);
//     validateDate(currentRow.querySelector('.date-field'));
//     closeModal();
//     updateSummary();
// }

// Call updateAllClientFields after saving modal to refresh dropdowns with new custom client
function saveModalEntry() {
    if (!currentRow) return;
    const modalInputs = document.querySelectorAll('#modalOverlay input, #modalOverlay select');
    const rowInputs = currentRow.querySelectorAll('input, select');
    
    for (let i = 0; i < modalInputs.length; i++) {
        if (rowInputs[i].tagName === 'INPUT' && rowInputs[i].type !== 'button') {
            rowInputs[i].value = modalInputs[i].value;
        } else if (rowInputs[i].tagName === 'SELECT') {
            rowInputs[i].value = modalInputs[i].value;
        }
    }
    calculateHours(currentRow);
    validateDate(currentRow.querySelector('.date-field'));
    closeModal();
    updateSummary();
    updateAllClientFields(); // Refresh all client dropdowns to include new custom client
}

function updateSummary() {
    const sections = document.querySelectorAll('.timesheet-section');
    let totalHours = 0;
    let billableHours = 0;
    let nonBillableHours = 0;

    sections.forEach(section => {
        const rows = section.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const hours = parseFloat(row.querySelector('.project-hours-field').value) || 0;
            totalHours += hours;
            if (row.querySelector('.billable-select').value === 'Yes') {
                billableHours += hours;
            } else if (row.querySelector('.billable-select').value === 'No') {
                nonBillableHours += hours;
            }
        });
    });

    const totalHoursElement = document.querySelector('.summary-section .total-hours .value');
    const billableHoursElement = document.querySelector('.summary-section .billable-hours .value');
    const nonBillableHoursElement = document.querySelector('.summary-section .non-billable-hours .value');
    if (totalHoursElement) totalHoursElement.textContent = totalHours.toFixed(2);
    if (billableHoursElement) billableHoursElement.textContent = billableHours.toFixed(2);
    if (nonBillableHoursElement) nonBillableHoursElement.textContent = nonBillableHours.toFixed(2);
}

function exportTimesheetToExcel() {
    const wb = XLSX.utils.book_new();
    const employeeInfo = getEmployeeInfoForExport();
    let allData = [];

    allData.push(employeeInfo);

    const sections = document.querySelectorAll('.timesheet-section');
    sections.forEach((section) => {
        const weekPeriod = section.querySelector('.week-period select').value || '';
        const rows = section.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const inputs = row.querySelectorAll('input, select');
            const rowData = {
                'Employee ID': employeeInfo['Employee ID'],
                'Employee Name': employeeInfo['Employee Name'],
                'Designation': employeeInfo['Designation'],
                'Gender': employeeInfo['Gender'],
                'Partner': employeeInfo['Partner'],
                'Reporting Manager': employeeInfo['Reporting Manager'],
                // 'Department': document.getElementById('department').value || '',
                'Week Period': weekPeriod,
                'S.No': row.cells[0].textContent,
                'Date': inputs[0] ? inputs[0].value : '',
                'Location of Work': inputs[1] ? (inputs[1].value || inputs[1].querySelector('option:checked')?.value) : '',
                'Project Start Time': inputs[2] ? inputs[2].value : '',
                'Project End Time': inputs[3] ? inputs[3].value : '',
                'Punch In': inputs[4] ? inputs[4].value : '',
                'Punch Out': inputs[5] ? inputs[5].value : '',
                'Client': inputs[6] ? (inputs[6].value || inputs[6].querySelector('option:checked')?.value) : '',
                'Project': inputs[7] ? inputs[7].value : '',
                'Project Code': inputs[8] ? inputs[8].value : '',
                'Reporting Manager Entry': inputs[9] ? (inputs[9].value || inputs[9].querySelector('option:checked')?.value) : '',
                'Activity': inputs[10] ? inputs[10].value : '',
                'Project Hours': inputs[11] ? inputs[11].value : '',
                'Working Hours': inputs[12] ? inputs[12].value : '',
                'Billable': inputs[13] ? inputs[13].value : '',
                'Remarks': inputs[14] ? inputs[14].value : '',
                '3 HITS': document.getElementById('hits').value || '',
                '3 MISSES': document.getElementById('misses').value || '',
                'FEEDBACK FOR HR': document.getElementById('feedback_hr').value || '',
                'FEEDBACK FOR IT': document.getElementById('feedback_it').value || '',
                'FEEDBACK FOR CRM': document.getElementById('feedback_crm').value || '',
                'FEEDBACK FOR OTHERS': document.getElementById('feedback_others').value || ''
            };
            allData.push(rowData);
        });
    });

    const ws = XLSX.utils.json_to_sheet(allData);
    XLSX.utils.book_append_sheet(wb, ws, 'Timesheet');
    XLSX.writeFile(wb, `Timesheet_${document.getElementById('employeeId').value || 'User'}_${new Date().toISOString().split('T')[0]}.xlsx`);
}

function getEmployeeInfoForExport() {
    return {
        'Employee ID': document.getElementById('employeeId').value || '',
        'Employee Name': document.getElementById('employeeName').value || '',
        'Designation': document.getElementById('designation').value || '',
        'Gender': document.getElementById('gender').value || '',
        'Partner': document.getElementById('partner').value || '',
        'Reporting Manager': document.getElementById('reportingManager').value || '',
        // 'Department': document.getElementById('department').value || '',
        'Week Period': '',
        'S.No': '',
        'Date': '',
        'Location of Work': '',
        'Project Start Time': '',
        'Project End Time': '',
        'Punch In': '',
        'Punch Out': '',
        'Client': '',
        'Project': '',
        'Project Code': '',
        'Reporting Manager Entry': '',
        'Activity': '',
        'Project Hours': '',
        'Working Hours': '',
        'Billable': '',
        'Remarks': '',
        '3 HITS': '',
        '3 MISSES': '',
        'FEEDBACK FOR HR': '',
        'FEEDBACK FOR IT': '',
        'FEEDBACK FOR CRM': '',
        'FEEDBACK FOR OTHERS': ''
    };
}

async function exportHistoryToExcel() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_URL}/timesheets/${loggedInEmployeeId}`, {
            headers: getHeaders()
        });
        if (!response.ok) {
            throw new Error('Failed to fetch history for export');
        }
        const data = await response.json();
        const entries = Array.isArray(data.Data) ? data.Data : data.Data ? [data.Data] : [];

        const wb = XLSX.utils.book_new();
        const employeeInfo = getEmployeeInfoForExport();
        let allData = [];

        allData.push(employeeInfo);

        entries.forEach(entry => {
            const rowData = {
                'Employee ID': employeeInfo['Employee ID'],
                'Employee Name': employeeInfo['Employee Name'],
                'Designation': employeeInfo['Designation'],
                'Gender': employeeInfo['Gender'],
                'Partner': employeeInfo['Partner'],
                'Reporting Manager': employeeInfo['Reporting Manager'],
                'Week Period': entry.weekPeriod || '',
                'S.No': '',
                'Date': entry.date || '',
                'Location of Work': entry.location || '',
                'Project Start Time': entry.projectStartTime || '',
                'Project End Time': entry.projectEndTime || '',
                'Punch In': entry.punchIn || '',
                'Punch Out': entry.punchOut || '',
                'Client': entry.client || '',
                'Project': entry.project || '',
                'Project Code': entry.projectCode || '',
                'Reporting Manager Entry': entry.reportingManagerEntry || '',
                'Activity': entry.activity || '',
                'Project Hours': entry.hours || '',
                'Working Hours': entry.workingHours || '',
                'Billable': entry.billable || '',
                'Remarks': entry.remarks || '',
                '3 HITS': entry.hits || '',
                '3 MISSES': entry.misses || '',
                'FEEDBACK FOR HR': entry.feedback_hr || '',
                'FEEDBACK FOR IT': entry.feedback_it || '',
                'FEEDBACK FOR CRM': entry.feedback_crm || '',
                'FEEDBACK FOR OTHERS': entry.feedback_others || '',
                'Total Hours': data.totalHours || '0.00',
                'Total Billable Hours': data.totalBillableHours || '0.00',
                'Total Non-Billable Hours': data.totalNonBillableHours || '0.00'
            };
            allData.push(rowData);
        });

        const ws = XLSX.utils.json_to_sheet(allData);
        XLSX.utils.book_append_sheet(wb, ws, 'History');
        XLSX.writeFile(wb, `History_${document.getElementById('employeeId').value || 'User'}_${new Date().toISOString().split('T')[0]}.xlsx`);
    } catch (error) {
        console.error('Error exporting history:', error);
        showPopup('Failed to export history: ' + error.message, true);
    }
}

async function saveDataToMongo() {
    showLoading();
    const employeeId = document.getElementById('employeeId').value.trim();
    if (!employeeId) {
        hideLoading();
        showPopup('Please enter Employee ID', true);
        return;
    }

    const timesheetData = [];
    const employeeDataObj = {
        employeeId: employeeId,
        employeeName: document.getElementById('employeeName').value || '',
        designation: document.getElementById('designation').value || '',
        gender: document.getElementById('gender').value || '',
        partner: document.getElementById('partner').value || '',
        reportingManager: document.getElementById('reportingManager').value || '',
        weekPeriod: '',
        date: '',
        location: '',
        projectStartTime: '',
        projectEndTime: '',
        punchIn: '',
        punchOut: '',
        client: '',
        project: '',
        projectCode: '',
        reportingManagerEntry: '',
        activity: '',
        hours: '',
        workingHours: '',
        billable: '',
        remarks: '',
        hits: document.getElementById('hits').value || '',
        misses: document.getElementById('misses').value || '',
        feedback_hr: document.getElementById('feedback_hr').value || '',
        feedback_it: document.getElementById('feedback_it').value || '',
        feedback_crm: document.getElementById('feedback_crm').value || '',
        feedback_others: document.getElementById('feedback_others').value || '',
        totalHours: document.querySelector('.summary-section .total-hours .value').textContent || '0.00',
        totalBillableHours: document.querySelector('.summary-section .billable-hours .value').textContent || '0.00',
        totalNonBillableHours: document.querySelector('.summary-section .non-billable-hours .value').textContent || '0.00'
    };

    const sections = document.querySelectorAll('.timesheet-section');
    let hasInvalidDates = false;
    sections.forEach(section => {
        const weekPeriod = section.querySelector('.week-period select').value || '';
        const rows = section.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const inputs = row.querySelectorAll('input, select');
            if (inputs.length < 15) return;
            const dateInput = inputs[0];
            const selectedWeek = weekOptions.find(opt => opt.value === weekPeriod);
            if (selectedWeek) {
                const inputDate = new Date(dateInput.value);
                if (inputDate < selectedWeek.start || inputDate > selectedWeek.end) {
                    hasInvalidDates = true;
                    return;
                }
            }
            console.log("Inputs:", inputs);
            const rowData = {
                employeeId: employeeId,
                employeeName: document.getElementById('employeeName').value || '',
                designation: document.getElementById('designation').value || '',
                gender: document.getElementById('gender').value || '',
                partner: document.getElementById('partner').value || '',
                reportingManager: document.getElementById('reportingManager').value || '',
                weekPeriod: weekPeriod,
                date: inputs[0] ? inputs[0].value : '',
                location: inputs[1] ? (inputs[1].value || inputs[1].querySelector('option:checked')?.value) : '',
                projectStartTime: inputs[2] ? inputs[2].value : '',
                projectEndTime: inputs[3] ? inputs[3].value : '',
                punchIn: inputs[4] ? inputs[4].value : '',
                punchOut: inputs[5] ? inputs[5].value : '',
                client: inputs[6] ? (inputs[6].value || inputs[6].querySelector('option:checked')?.value || '') : '',
                project: inputs[7] ? inputs[7].value : '',
                projectCode: inputs[8] ? inputs[8].value : '',
                reportingManagerEntry: inputs[9] ? (inputs[9].value || inputs[9].querySelector('option:checked')?.value || '') : '',
                activity: inputs[10] ? inputs[10].value : '',
                hours: inputs[11] ? inputs[11].value : '',
                workingHours: inputs[12] ? inputs[12].value : '',
                billable: inputs[13] ? inputs[13].value : '',
                remarks: inputs[14] ? inputs[14].value : '',
                hits: document.getElementById('hits').value || '',
                misses: document.getElementById('misses').value || '',
                feedback_hr: document.getElementById('feedback_hr').value || '',
                feedback_it: document.getElementById('feedback_it').value || '',
                feedback_crm: document.getElementById('feedback_crm').value || '',
                feedback_others: document.getElementById('feedback_others').value || '',
                totalHours: document.querySelector('.summary-section .total-hours .value').textContent || '0.00',
                totalBillableHours: document.querySelector('.summary-section .billable-hours .value').textContent || '0.00',
                totalNonBillableHours: document.querySelector('.summary-section .non-billable-hours .value').textContent || '0.00'
            };
            timesheetData.push(rowData);
        });
    });

    if (hasInvalidDates) {
        hideLoading();
        showPopup('Please correct all dates to be within their respective week periods.', true);
        return;
    }

    if (timesheetData.length === 0) {
        timesheetData.push(employeeDataObj);
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_URL}/save_timesheets`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(timesheetData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Failed to save data: ${errorData.detail || 'Unknown error'}`);
        }

        const result = await response.json();
        hideLoading();
        showPopup('Timesheet saved successfully!');
        // clearTimesheet();
    } catch (error) {
        console.error('Error saving data:', error);
        hideLoading();
        showPopup(`Failed to save timesheet: ${error.message}`, true);
    }
}

function clearTimesheet() {
    showPopup('Timesheet cleared!');
    document.getElementById('hits').value = '';
    document.getElementById('misses').value = '';
    document.getElementById('feedback_hr').value = '';
    document.getElementById('feedback_it').value = '';
    document.getElementById('feedback_crm').value = '';
    document.getElementById('feedback_others').value = '';
    setTimeout(() => {
        window.location.reload();
    }, 3000);
}

function toggleNavMenu() {
    const navMenu = document.getElementById('navMenu');
    navMenu.classList.toggle('active');
}

async function logout() {
    showLoading("Logging out...");
    try {
        const token = localStorage.getItem('access_token');
        await fetch(`${API_URL}/logout`, {
            method: 'POST',
            headers: getHeaders()
        });
    } catch (error) {
        console.error('Error during logout:', error);
    } finally {
        hideLoading();
        localStorage.removeItem('access_token');
        localStorage.removeItem('loggedInEmployeeId');
        window.location.href = '/static/login.html';
    }
}


async function showSection(section) {
    document.getElementById('timesheetSection').style.display = section === 'timesheet' ? 'block' : 'none';
    document.getElementById('historySection').style.display = section === 'history' ? 'block' : 'none';
    document.querySelectorAll('.nav-menu a').forEach(a => a.classList.remove('active'));
    document.querySelector(`.nav-menu a[onclick*="${section}"]`).classList.add('active');

    if (section === 'history') {
        try {
            showLoading("Fetching History...");
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${API_URL}/timesheets/${loggedInEmployeeId}`, {
                headers: getHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch history');
            }

            const data = await response.json();
            console.log('API Response:', data); // Debug log to check structure
            const historyContent = document.getElementById('historyContent');
            historyContent.innerHTML = '';

            // Update summary hours in history section
            const totalHoursElement = document.querySelector('.history-summary .total-hours .value');
            const billableHoursElement = document.querySelector('.history-summary .billable-hours .value');
            const nonBillableHoursElement = document.querySelector('.history-summary .non-billable-hours .value');

            if (totalHoursElement && billableHoursElement && nonBillableHoursElement) {
                // Check if summary data is at root level
                totalHoursElement.textContent = (data.totalHours || 0).toFixed(2);
                billableHoursElement.textContent = (data.totalBillableHours || 0).toFixed(2);
                nonBillableHoursElement.textContent = (data.totalNonBillableHours || 0).toFixed(2);

                // Fallback: Check if summary data is within data.Data (e.g., aggregated from entries)
                if (!data.totalHours && data.Data && Array.isArray(data.Data)) {
                    const summary = data.Data.reduce(
                        (acc, entry) => {
                            const hours = parseFloat(entry.hours) || 0;
                            acc.totalHours += hours;
                            if (entry.billable === 'Yes') {
                                acc.totalBillableHours += hours;
                            } else if (entry.billable === 'No') {
                                acc.totalNonBillableHours += hours;
                            }
                            return acc;
                        },
                        { totalHours: 0, totalBillableHours: 0, totalNonBillableHours: 0 }
                    );
                    totalHoursElement.textContent = summary.totalHours.toFixed(2);
                    billableHoursElement.textContent = summary.totalBillableHours.toFixed(2);
                    nonBillableHoursElement.textContent = summary.totalNonBillableHours.toFixed(2);
                }
            }

            if (!data.Data || data.Data.length === 0) {
                historyContent.innerHTML = '<p>No timesheet entries found.</p>';
                hideLoading();
                return;
            }

            // Rest of the existing code for rendering history table and feedback
            const groupedByWeek = {};
            data.Data.forEach(entry => {
                const week = entry.weekPeriod || 'No Week';
                if (!groupedByWeek[week]) {
                    groupedByWeek[week] = [];
                }
                groupedByWeek[week].push(entry);
            });

            Object.keys(groupedByWeek).forEach((week, index) => {
                const weekDiv = document.createElement('div');
                weekDiv.className = 'history-week';
                weekDiv.innerHTML = `<h3>Week Period: ${week}</h3>`;

                const tableWrapper = document.createElement('div');
                tableWrapper.className = 'table-responsive';
                const table = document.createElement('table');
                table.className = 'timesheet-table history-table';
                table.innerHTML = `
                    <thead>
                        <tr>
                            <th class="col-narrow col-sno">S.No</th>
                            <th class="col-medium col-date">Date</th>
                            <th class="col-wide col-location">Location of Work</th>
                            <th class="col-medium col-project-start">Project Start Time</th>
                            <th class="col-medium col-project-end">Project End Time</th>
                            <th class="col-medium col-punch-in">Punch In</th>
                            <th class="col-medium col-punch-out">Punch Out</th>
                            <th class="col-wide col-client">Client</th>
                            <th class="col-wide col-project">Project</th>
                            <th class="col-project col-project-code">Project Code</th>
                            <th class="col-wide col-reporting-manager">Reporting Manager</th>
                            <th class="col-wide col-activity">Activity</th>
                            <th class="col-narrow col-project-hours">Project Hours</th>
                            <th class="col-narrow col-working-hours">Working Hours</th>
                            <th class="col-medium col-billable">Billable</th>
                            <th class="col-wide col-remarks">Remarks</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                `;
                const tbody = table.querySelector('tbody');

                groupedByWeek[week].forEach((entry, rowIndex) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="col-sno">${rowIndex + 1}</td>
                        <td class="col-date">${entry.date || ''}</td>
                        <td class="col-location">${entry.location || ''}</td>
                        <td class="col-project-start">${entry.projectStartTime || ''}</td>
                        <td class="col-project-end">${entry.projectEndTime || ''}</td>
                        <td class="col-punch-in">${entry.punchIn || ''}</td>
                        <td class="col-punch-out">${entry.punchOut || ''}</td>
                        <td class="col-client">${entry.client || ''}</td>
                        <td class="col-project">${entry.project || ''}</td>
                        <td class="col-project-code">${entry.projectCode || ''}</td>
                        <td class="col-reporting-manager">${entry.reportingManagerEntry || ''}</td>
                        <td class="col-activity">${entry.activity || ''}</td>
                        <td class="col-project-hours">${entry.hours || ''}</td>
                        <td class="col-working-hours">${entry.workingHours || ''}</td>
                        <td class="col-billable">${entry.billable || ''}</td>
                        <td class="col-remarks">${entry.remarks || ''}</td>
                    `;
                    tbody.appendChild(row);
                });

                tableWrapper.appendChild(table);
                weekDiv.appendChild(tableWrapper);
                historyContent.appendChild(weekDiv);

                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'history-feedback';
                feedbackDiv.innerHTML = `
                    <h4>Feedback for Week: ${week}</h4>
                    <div class="feedback-item"><strong>3 HITS:</strong> ${groupedByWeek[week][0].hits || ''}</div>
                    <div class="feedback-item"><strong>3 MISSES:</strong> ${groupedByWeek[week][0].misses || ''}</div>
                    <div class="feedback-item"><strong>FEEDBACK FOR HR:</strong> ${groupedByWeek[week][0].feedback_hr || ''}</div>
                    <div class="feedback-item"><strong>FEEDBACK FOR IT:</strong> ${groupedByWeek[week][0].feedback_it || ''}</div>
                    <div class="feedback-item"><strong>FEEDBACK FOR CRM:</strong> ${groupedByWeek[week][0].feedback_crm || ''}</div>
                    <div class="feedback-item"><strong>FEEDBACK FOR OTHERS:</strong> ${groupedByWeek[week][0].feedback_others || ''}</div>
                `;
                historyContent.appendChild(feedbackDiv);
            });

            hideLoading();
        } catch (error) {
            console.error('Error fetching history:', error);
            hideLoading();
            showPopup('Failed to load history: ' + error.message, true);
        }
    }
}


function editHistoryRow(button, entryId) {
    const row = button.closest('tr');
    const cells = row.querySelectorAll('td');
    const originalHtml = row.innerHTML;
    row.dataset.originalHtml = originalHtml;
    row.dataset.entryId = entryId;

    const data = {
        date: cells[1].textContent,
        location: cells[2].textContent,
        projectStartTime: cells[3].textContent,
        projectEndTime: cells[4].textContent,
        punchIn: cells[5].textContent,
        punchOut: cells[6].textContent,
        client: cells[7].textContent,
        project: cells[8].textContent,
        projectCode: cells[9].textContent,
        reportingManagerEntry: cells[10].textContent,
        activity: cells[11].textContent,
        hours: cells[12].textContent,
        workingHours: cells[13].textContent,
        billable: cells[14].textContent,
        remarks: cells[15].textContent,
        created_time: cells[16].textContent,
        updated_time: cells[17].textContent
    };

    cells[0].innerHTML = `
    <button class="cancel-btn" onclick="cancelEdit(this)">Cancel</button>
    <button class="update-btn" onclick="updateHistoryRow(this, '${entryId}')">Update</button>
`;
    cells[1].innerHTML = `<input type="date" value="${data.date}" class="date-field form-input">`;
    cells[2].innerHTML = `<select class="location-select form-input">
        <option value="Office" ${data.location === 'Office' ? 'selected' : ''}>Office</option>
        <option value="Client Site" ${data.location === 'Client Site' ? 'selected' : ''}>Client Site</option>
        <option value="Work From Home" ${data.location === 'Work From Home' ? 'selected' : ''}>Work From Home</option>
        <option value="Field Work" ${data.location === 'Field Work' ? 'selected' : ''}>Field Work</option>
    </select>`;
    cells[3].innerHTML = `<input type="time" value="${data.projectStartTime}" class="project-start form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))">`;
    cells[4].innerHTML = `<input type="time" value="${data.projectEndTime}" class="project-end form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))">`;
    cells[5].innerHTML = `<input type="time" value="${data.punchIn}" class="punch-in form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))">`;
    cells[6].innerHTML = `<input type="time" value="${data.punchOut}" class="punch-out form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))">`;
    cells[7].innerHTML = `<select class="client-field client-select form-input" data-projects="[]" onchange="handleClientChange(this)"><option value="">Select Client</option></select>`;
    cells[7].querySelector('select').value = data.client;
    cells[8].innerHTML = `<input type="text" value="${data.project}" class="project-field form-input">`;
    cells[9].innerHTML = `<input type="text" value="${data.projectCode}" class="project-code form-input" readonly>`;
    cells[10].innerHTML = `<select class="reporting-manager-field reporting-manager-select form-input" onchange="handleReportingManagerChange(this)"><option value="">Select Reporting Manager</option></select>`;
    cells[10].querySelector('select').value = data.reportingManagerEntry;
    cells[11].innerHTML = `<input type="text" value="${data.activity}" class="activity-field form-input">`;
    cells[12].innerHTML = `<input type="number" value="${data.hours}" class="project-hours-field form-input" readonly>`;
    cells[13].innerHTML = `<input type="number" value="${data.workingHours}" class="working-hours-field form-input" readonly>`;
    cells[14].innerHTML = `<select class="billable-select form-input">
        <option value="Yes" ${data.billable === 'Yes' ? 'selected' : ''}>Billable</option>
        <option value="No" ${data.billable === 'No' ? 'selected' : ''}>Non-Billable</option>
    </select>`;
    cells[15].innerHTML = `<input type="text" value="${data.remarks}" class="remarks-field form-input">`;
    cells[16].innerHTML = data.created_time;
    cells[17].innerHTML = data.updated_time;
    updateAllClientFields();
    updateAllReportingManagerFields();
}

function cancelEdit(button) {
    const row = button.closest('tr');
    row.innerHTML = row.dataset.originalHtml;
    delete row.dataset.originalHtml;
    delete row.dataset.entryId;
    updateAllClientFields();
    updateAllReportingManagerFields();
}

async function updateHistoryRow(button, entryId) {
    const row = button.closest('tr');
    if (!row) return;

    const cells = row.querySelectorAll('td');
    const dateCell = cells[1];
    const locationCell = cells[2];
    const projectStartCell = cells[3];
    const projectEndCell = cells[4];
    const punchInCell = cells[5];
    const punchOutCell = cells[6];
    const clientCell = cells[7];
    const projectCell = cells[8];
    const projectCodeCell = cells[9];
    const reportingCell = cells[10];
    const activityCell = cells[11];
    const hoursCell = cells[12];
    const workingHoursCell = cells[13];
    const billableCell = cells[14];
    const remarksCell = cells[15];

    function getCellValue(cell) {
        const input = cell.querySelector('input');
        const select = cell.querySelector('select');
        const textarea = cell.querySelector('textarea');
        if (input) return input.value;
        if (select) return select.value;
        if (textarea) return textarea.value;
        return cell.textContent.trim();
    }

    const updatedEntry = {
        date: getCellValue(dateCell),
        location: getCellValue(locationCell),
        projectStartTime: getCellValue(projectStartCell),
        projectEndTime: getCellValue(projectEndCell),
        punchIn: getCellValue(punchInCell),
        punchOut: getCellValue(punchOutCell),
        client: getCellValue(clientCell),
        project: getCellValue(projectCell),
        projectCode: getCellValue(projectCodeCell),
        reportingManagerEntry: getCellValue(reportingCell),
        activity: getCellValue(activityCell),
        hours: getCellValue(hoursCell),
        workingHours: getCellValue(workingHoursCell),
        billable: getCellValue(billableCell),
        remarks: getCellValue(remarksCell)
    };

    console.log('Updating entry with data:', updatedEntry);

    try {
        const token = localStorage.getItem('access_token');
        if (!token) throw new Error('No token found');
        const response = await fetch(`${API_URL}/update_timesheet/${loggedInEmployeeId}/${entryId}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(updatedEntry)
        });
        if (!response.ok) {
            let errorMsg = response.statusText;
            try {
                const errorData = await response.json();
                errorMsg = errorData.detail || errorData.message || errorMsg;
            } catch (e) {
                // Ignore JSON parse error
            }
            throw new Error(`Failed to update entry: ${errorMsg}`);
        }
        const result = await response.json();
        if (result.success) {
            showPopup(`Entry updated successfully at ${new Date().toLocaleString()}!`);
            await loadHistory();
        } else {
            showPopup('Failed to update entry.', true);
        }
    } catch (error) {
        console.error('Error updating entry:', error);
        showPopup(`Failed to update entry: ${error.message}`, true);
    }
}

function updateDateValidations(sectionId) {
    const section = document.getElementById(sectionId);
    const dateInputs = section.querySelectorAll('.date-field');
    dateInputs.forEach(input => validateDate(input));
}

function validateTimes(row, isModal = false) {
    let isValid = true;
    let errorMessage = '';

    if (isModal) {
        const projectStart = document.getElementById('modalInput5').value;
        const projectEnd = document.getElementById('modalInput6').value;
        const punchIn = document.getElementById('modalInput3').value;
        const punchOut = document.getElementById('modalInput4').value;

        if (projectStart && projectEnd) {
            const [startH, startM] = projectStart.split(':').map(Number);
            const [endH, endM] = projectEnd.split(':').map(Number);
            const startMinutes = startH * 60 + startM;
            const endMinutes = endH * 60 + endM;
            if (endMinutes <= startMinutes) {
                isValid = false;
                errorMessage = 'Project End Time must be later than Project Start Time.';
                document.getElementById('modalInput6').classList.add('validation-error');
                showValidationMessage(document.getElementById('modalInput6'), errorMessage);
            } else {
                document.getElementById('modalInput6').classList.remove('validation-error');
                clearValidationMessage(document.getElementById('modalInput6'));
            }
        }

        if (punchIn && punchOut) {
            const [inH, inM] = punchIn.split(':').map(Number);
            const [outH, outM] = punchOut.split(':').map(Number);
            const inMinutes = inH * 60 + inM;
            const outMinutes = outH * 60 + outM;
            if (outMinutes <= inMinutes) {
                isValid = false;
                errorMessage = errorMessage || 'Punch Out must be later than Punch In.';
                document.getElementById('modalInput4').classList.add('validation-error');
                showValidationMessage(document.getElementById('modalInput4'), errorMessage);
            } else {
                document.getElementById('modalInput4').classList.remove('validation-error');
                clearValidationMessage(document.getElementById('modalInput4'));
            }
        }
    } else {
        const projectStart = row.querySelector('.project-start')?.value;
        const projectEnd = row.querySelector('.project-end')?.value;
        const punchIn = row.querySelector('.punch-in')?.value;
        const punchOut = row.querySelector('.punch-out')?.value;

        if (projectStart && projectEnd) {
            const [startH, startM] = projectStart.split(':').map(Number);
            const [endH, endM] = projectEnd.split(':').map(Number);
            const startMinutes = startH * 60 + startM;
            const endMinutes = endH * 60 + endM;
            if (endMinutes <= startMinutes) {
                isValid = false;
                errorMessage = 'Project End Time must be later than Project Start Time.';
                row.querySelector('.project-end').classList.add('validation-error');
                showValidationMessage(row.querySelector('.project-end'), errorMessage);
            } else {
                row.querySelector('.project-end').classList.remove('validation-error');
                clearValidationMessage(row.querySelector('.project-end'));
            }
        }

        if (punchIn && punchOut) {
            const [inH, inM] = punchIn.split(':').map(Number);
            const [outH, outM] = punchOut.split(':').map(Number);
            const inMinutes = inH * 60 + inM;
            const outMinutes = outH * 60 + outM;
            if (outMinutes <= inMinutes) {
                isValid = false;
                errorMessage = errorMessage || 'Punch Out must be later than Punch In.';
                row.querySelector('.punch-out').classList.add('validation-error');
                showValidationMessage(row.querySelector('.punch-out'), errorMessage);
            } else {
                row.querySelector('.punch-out').classList.remove('validation-error');
                clearValidationMessage(row.querySelector('.punch-out'));
            }
        }
    }

    if (!isValid && errorMessage) {
        showPopup(errorMessage, true);
    }

    return isValid;
}

let isExiting = false;
window.addEventListener('beforeunload', function(e) {
    if (!isExiting) {
        e.preventDefault();
        e.returnValue = '';
        showExitConfirmation();
        return 'Are you sure you want to leave?';
    }
});
document.addEventListener('keydown', function(e) {
    if (e.key === 'Backspace' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        showExitConfirmation();
    }
});
function showExitConfirmation() {
    const exitPopup = document.getElementById('exitConfirmation');
    if (exitPopup) {
        exitPopup.style.display = 'block';
    }
}
function cancelExit() {
    const exitPopup = document.getElementById('exitConfirmation');
    if (exitPopup) {
        exitPopup.style.display = 'none';
    }
}
function confirmExit() {
    isExiting = true;
    logout();
}

// New function to copy row data
function copyRow(button) {
    const row = button.closest('tr');
    copiedData = {};
    const inputs = row.querySelectorAll('input, select');
    inputs.forEach((input, index) => {
        if (input.type === 'button' || input.classList.contains('copy-btn') || input.classList.contains('paste-btn')) return;
        copiedData[`field${index}`] = input.type === 'select' ? input.value : input.value;
    });
    showPopup('Row data copied!');
}

// New function to paste row data
function pasteRow(button) {
    if (!copiedData) {
        showPopup('No data copied to paste!', true);
        return;
    }
    const row = button.closest('tr');
    const inputs = row.querySelectorAll('input, select');
    inputs.forEach((input, index) => {
        if (input.type === 'button' || input.classList.contains('copy-btn') || input.classList.contains('paste-btn')) return;
        const fieldKey = `field${index}`;
        if (copiedData[fieldKey] !== undefined) {
            input.value = copiedData[fieldKey];
            if (input.classList.contains('date-field')) validateDate(input);
            if (input.classList.contains('project-start') || input.classList.contains('project-end') ||
                input.classList.contains('punch-in') || input.classList.contains('punch-out')) {
                validateTimes(row);
                calculateHours(row);
            }
            if (input.classList.contains('client-field')) handleClientChange(input);
            if (input.classList.contains('reporting-manager-field')) handleReportingManagerChange(input);
        }
    });
    updateSummary();
    showPopup('Row data pasted!');
}


function pasteAboveCell(sectionId) {
    const tbody = document.getElementById(`timesheetBody_${sectionId.split('_')[1]}`);
    if (!tbody) {
        showPopup('Table body not found!', true);
        return;
    }
    
    const rows = tbody.querySelectorAll('tr');
    if (rows.length === 0) {
        showPopup('No rows to duplicate! Adding a new row.', true);
        addRow(sectionId);
        return;
    }
    
    const lastRow = rows[rows.length - 1];
    const newRow = document.createElement('tr');
    newRow.innerHTML = lastRow.innerHTML; // Copy HTML structure and content
    
    // Insert the new row into the DOM before validations
    tbody.insertBefore(newRow, lastRow.nextSibling);
    
    // Get inputs from the new row and last row
    const newInputs = newRow.querySelectorAll('input, select');
    const lastInputs = lastRow.querySelectorAll('input, select');
    
    // Copy values and handle validations
    newInputs.forEach((input, index) => {
        if (input.type === 'button' || input.classList.contains('copy-btn') || 
            input.classList.contains('paste-btn') || input.classList.contains('delete-btn')) {
            return; // Skip buttons
        }
        if (lastInputs[index]) {
            input.value = lastInputs[index].value; // Copy value from last row
            if (input.classList.contains('date-field')) {
                const weekSelect = document.getElementById(`weekPeriod_${sectionId.split('_')[1]}`);
                if (weekSelect) {
                    const selectedWeek = weekOptions.find(opt => opt.value === weekSelect.value);
                    if (selectedWeek) {
                        const currentDate = new Date(input.value);
                        const weekEnd = new Date(selectedWeek.end);
                        if (currentDate < weekEnd) {
                            currentDate.setDate(currentDate.getDate() + 1);
                            input.value = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
                        }
                        // Validate date after DOM insertion
                        validateDate(input);
                    }
                }
            }
            if (input.classList.contains('project-start') || input.classList.contains('project-end') ||
                input.classList.contains('punch-in') || input.classList.contains('punch-out')) {
                validateTimes(newRow);
                calculateHours(newRow);
            }
            if (input.classList.contains('client-field')) {
                input.dataset.projects = lastInputs[index].dataset.projects; // Copy project data
                handleClientChange(input);
            }
            if (input.classList.contains('reporting-manager-field')) {
                handleReportingManagerChange(input);
            }
        }
    });
    
    updateRowNumbers(tbody.id);
    updateSummary();
    showPopup('Row duplicated above last row!');
}





function addWeekSection() {
    sectionCount++;
    const sectionsDiv = document.getElementById('timesheetSections');
    const sectionId = `section_${sectionCount}`;
    
    const section = document.createElement('div');
    section.className = 'timesheet-section';
    section.id = sectionId;
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-week-btn';
    deleteBtn.textContent = 'Delete Week';
    deleteBtn.onclick = () => deleteWeekSection(sectionId);
    section.appendChild(deleteBtn);
    
    const weekPeriod = document.createElement('div');
    weekPeriod.className = 'week-period form-group';
    weekPeriod.innerHTML = `
        <label>Week Period ${sectionCount}</label>
    `;
    const select = document.createElement('select');
    select.id = `weekPeriod_${sectionCount}`;
    select.onchange = () => {
        updateSummary();
        updateDateValidations(sectionId);
        updateExistingRowDates(sectionId);
    };
    weekOptions.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.text;
        select.appendChild(option);
    });
    if (weekOptions.length > 0) {
        select.value = weekOptions[0].value;
        setTimeout(() => {
            select.onchange();
        }, 100);
    }
    weekPeriod.appendChild(select);
    section.appendChild(weekPeriod);
    
    const tableWrapper = document.createElement('div');
    tableWrapper.className = 'table-responsive';
    const table = document.createElement('table');
    table.className = 'timesheet-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th class="col-narrow col-sno">S.No</th>
                <th class="col-narrow col-add">Add</th>
                <th class="col-narrow col-action">Action</th>
                <th class="col-medium col-date">Date</th>
                <th class="col-wide col-location">Location of Work</th>
                <th class="col-medium col-project-start">Project Start Time</th>
                <th class="col-medium col-project-end">Project End Time</th>
                <th class="col-medium col-punch-in">Punch In</th>
                <th class="col-medium col-punch-out">Punch Out</th>
                <th class="col-wide col-client">Client</th>
                <th class="col-wide col-project">Project</th>
                <th class="col-project col-project-code">Project Code</th>
                <th class="col-wide col-reporting-manager">Reporting Manager</th>
                <th class="col-wide col-activity">Activity</th>
                <th class="col-narrow col-project-hours">Project Hours</th>
                <th class="col-narrow col-working-hours">Working Hours</th>
                <th class="col-medium col-billable">Billable</th>
                <th class="col-wide col-remarks">Remarks</th>
                <th class="col-narrow col-delete">Action</th>
            </tr>
        </thead>
        <tbody id="timesheetBody_${sectionCount}"></tbody>
    `;
    tableWrapper.appendChild(table);
    section.appendChild(tableWrapper);
    
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'button-container';
    
    const addRowBtn = document.createElement('button');
    addRowBtn.className = 'add-row-btn';
    addRowBtn.textContent = '+ Add New Entry';
    addRowBtn.onclick = () => addRow(sectionId);
    buttonContainer.appendChild(addRowBtn);
    
    const pasteAboveBtn = document.createElement('button');
    pasteAboveBtn.className = 'paste-above-btn';
    pasteAboveBtn.textContent = 'Paste Above Cell';
    pasteAboveBtn.onclick = () => pasteAboveCell(sectionId);
    buttonContainer.appendChild(pasteAboveBtn);
    
    section.appendChild(buttonContainer);
    
    sectionsDiv.appendChild(section);
    addRow(sectionId);
    updateAllClientFields();
    updateAllReportingManagerFields();
    updateDateValidations(sectionId);
}

function addRow(sectionId) {
    const tbody = document.getElementById(`timesheetBody_${sectionId.split('_')[1]}`);
    if (!tbody) return;
    const rows = tbody.querySelectorAll('tr');
    const rowCount = rows.length + 1;
    
    const weekSelect = document.getElementById(`weekPeriod_${sectionId.split('_')[1]}`);
    const selectedWeekValue = weekSelect.value;
    const selectedWeek = weekOptions.find(opt => opt.value === selectedWeekValue);
    
    let defaultDate = new Date().toISOString().split('T')[0];
    if (selectedWeek && selectedWeek.start) {
        const weekStart = new Date(selectedWeek.start);
        defaultDate = `${weekStart.getFullYear()}-${String(weekStart.getMonth() + 1).padStart(2, '0')}-${String(weekStart.getDate()).padStart(2, '0')}`;
    } else if (weekOptions.length > 0) {
        const firstWeek = weekOptions[0];
        const weekStart = new Date(firstWeek.start);
        defaultDate = `${weekStart.getFullYear()}-${String(weekStart.getMonth() + 1).padStart(2, '0')}-${String(weekStart.getDate()).padStart(2, '0')}`;
    }
    
    console.log(`Adding row for section ${sectionId}, week: ${selectedWeekValue}, default date: ${defaultDate}`);
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td class="col-sno" style="min-width: 60px;">${rowCount}</td>
        <td class="col-add" style="min-width: 60px;"><button class="eye-btn" onclick="openModal(this, false)"><i class="fas fa-eye"></i></button></td>
        <td class="col-action" style="min-width: 120px;">
            <button class="copy-btn" onclick="copyRow(this)"><i class="fas fa-copy"></i> Copy</button>
            <button class="paste-btn" onclick="pasteRow(this)"><i class="fas fa-paste"></i> Paste</button>
        </td>
        <td class="col-date" style="min-width: 120px;"><input type="date" value="${defaultDate}" class="date-field form-input" onchange="validateDate(this); updateSummary()"></td>
        <td class="clo-location" style="min-width: 200px;"><select class="location-select form-input" onchange="updateSummary()">
            <option value="Office">Office</option>
            <option value="Client Site">Client Site</option>
            <option value="Work From Home">Work From Home</option>
            <option value="Field Work">Field Work</option>
        </select></td>
        <td class="col-project-start" style="min-width: 120px;"><input type="time" class="project-start form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))"></td>
        <td class="col-project-end" style="min-width: 120px;"><input type="time" class="project-end form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))"></td>
        <td class="col-punch-in" style="min-width: 120px;"><input type="time" class="punch-in form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))"></td>
        <td class="col-punch-out" style="min-width: 120px;"><input type="time" class="punch-out form-input" onchange="validateTimes(this.closest('tr')); calculateHours(this.closest('tr'))"></td>
        <td class="col-client" style="min-width: 250px;"><select class="client-field client-select form-input" onchange="handleClientChange(this)" data-projects="[]"><option value="">Select Client</option></select></td>
        <td class="col-project" style="min-width: 200px;"><input type="text" class="project-field form-input" placeholder="Enter Project" oninput="updateSummary()"></td>
        <td class="col-project-code" style="min-width: 200px;"><input type="text" class="project-code form-input" readonly></td>
        <td class="col-reporting-manager" style="min-width: 200px;"><select class="reporting-manager-field reporting-manager-select form-input" onchange="handleReportingManagerChange(this)"><option value="">Select Reporting Manager</option></select></td>
        <td class="col-activity" style="min-width: 200px;"><input type="text" class="activity-field form-input" placeholder="Enter Activity" oninput="updateSummary()"></td>
        <td class="col-project-hours" style="min-width: 80px;"><input type="number" class="project-hours-field form-input" readonly></td>
        <td class="col-working-hours" style="min-width: 80px;"><input type="number" class="working-hours-field form-input" readonly></td>
        <td class="col-billable" style="min-width: 120px;"><select class="billable-select form-input" onchange="updateSummary()">
            <option value="Yes">Billable</option>
            <option value="No">Non-Billable</option>
        </select></td>
        <td class="col-remarks" style="min-width: 200px;"><input type="text" class="remarks-field form-input" placeholder="Additional notes"></td>
        <td class="col-delete" style="min-width: 80px;"><button class="delete-btn" onclick="deleteRow(this)">Delete</button></td>
    `;

    tbody.appendChild(row);
    updateAllClientFields();
    updateAllReportingManagerFields();
    
    const dateInput = row.querySelector('.date-field');
    if (dateInput) {
        validateDate(dateInput);
    }
    
    updateSummary();
}

function openModal(button, isReadOnly) {
    currentRow = button.closest('tr');
    const inputs = currentRow.querySelectorAll('input, select');
    const modal = document.getElementById('modalOverlay');
    modal.style.display = 'flex';

    const labels = [
        'Date', 'Location of Work', 'Punch In', 'Punch Out', 'Project Start Time', 'Project End Time',
        'Client', 'Project', 'Project Code', 'Reporting Manager', 'Activity', 'Project Hours', 'Working Hours', 'Billable', 'Remarks'
    ];
    
    for (let i = 0; i < inputs.length; i++) {
        const label = document.getElementById(`modalLabel${i + 1}`);
        const input = document.getElementById(`modalInput${i + 1}`);
        if (label && input) {
            label.textContent = labels[i];
            input.value = inputs[i].value || (inputs[i].tagName === 'SELECT' ? inputs[i].querySelector('option:checked')?.value : '');
            input.readOnly = isReadOnly;
            if (input.tagName === 'SELECT') {
                input.disabled = isReadOnly;
                if (i === 6) { // Client field
                    const select = inputs[i];
                    const relevantProjects = fetchProjectData(document.getElementById('partner')?.value || '', document.getElementById('reportingManager')?.value || '');
                    input.innerHTML = '<option value="">Select Client</option>';
                    relevantProjects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project['CLIENT NAME'];
                        option.textContent = project['CLIENT NAME'];
                        input.appendChild(option);
                    });
                    input.innerHTML += '<option value="Type here">Type here</option>';
                    input.value = select.value || '';
                    if (isReadOnly && input.value !== 'Type here') {
                        input.innerHTML = `<option value="${input.value}" selected>${input.value}</option>`;
                    }
                } else if (i === 13) { // Billable field
                    input.innerHTML = '<option value="Yes">Yes</option><option value="No">No</option>';
                    input.value = inputs[i].value || 'Yes';
                    if (isReadOnly) {
                        input.innerHTML = `<option value="${input.value}" selected>${input.value}</option>`;
                    }
                }
            }
        }
    }

    // Disable all inputs if read-only mode
    const modalInputs = modal.querySelectorAll('input, select');
    modalInputs.forEach(input => {
        input.readOnly = isReadOnly;
        if (input.tagName === 'SELECT') input.disabled = isReadOnly;
    });

    // Update modal fields dynamically
    updateModalClientFields();
    updateModalReportingManagerFields();
    validateModalDate(document.getElementById('modalInput1'));
    updateModalHours();

    // Set button behavior based on mode
    const addBtn = document.getElementById('modalAddBtn');
    const cancelBtn = document.getElementById('modalCancelBtn');
    if (isReadOnly) {
        addBtn.style.display = 'none';
        cancelBtn.textContent = 'Close';
    } else {
        addBtn.style.display = 'inline-block';
        cancelBtn.textContent = 'Cancel';
        addBtn.onclick = saveModalEntry;
    }
    cancelBtn.onclick = closeModal;
}


async function saveModalEntry() {
    if (!currentRow) return;
    const modalInputs = document.querySelectorAll('#modalOverlay input, #modalOverlay select');
    const rowInputs = currentRow.querySelectorAll('input, select');
    
    for (let i = 0; i < modalInputs.length; i++) {
        if (rowInputs[i].tagName === 'INPUT' && rowInputs[i].type !== 'button') {
            rowInputs[i].value = modalInputs[i].value;
        } else if (rowInputs[i].tagName === 'SELECT') {
            rowInputs[i].value = modalInputs[i].value;
        }
    }
    calculateHours(currentRow);
    validateDate(currentRow.querySelector('.date-field'));
    
    // Save to database
    const section = currentRow.closest('.timesheet-section');
    const weekPeriod = section.querySelector('.week-period select').value;
    const rowData = {
        employeeId: document.getElementById('employeeId').value,
        weekPeriod: weekPeriod,
        date: rowInputs[0].value,
        location: rowInputs[1].value,
        projectStartTime: rowInputs[2].value,
        projectEndTime: rowInputs[3].value,
        punchIn: rowInputs[4].value,
        punchOut: rowInputs[5].value,
        client: rowInputs[6].value,
        project: rowInputs[7].value,
        projectCode: rowInputs[8].value,
        reportingManagerEntry: rowInputs[9].value,
        activity: rowInputs[10].value,
        hours: rowInputs[11].value,
        workingHours: rowInputs[12].value,
        billable: rowInputs[13].value,
        remarks: rowInputs[14].value
    };
    await saveDataToMongo([rowData]); // Pass as array for consistency
    
    closeModal();
    updateSummary();
}

function saveModalEntry() {
    if (!currentRow) return;
    const modalInputs = document.querySelectorAll('#modalOverlay input, #modalOverlay select');
    const rowInputs = currentRow.querySelectorAll('input, select');
    
    for (let i = 0; i < modalInputs.length; i++) {
        if (rowInputs[i].tagName === 'INPUT' && rowInputs[i].type !== 'button') {
            rowInputs[i].value = modalInputs[i].value;
        } else if (rowInputs[i].tagName === 'SELECT') {
            rowInputs[i].value = modalInputs[i].value;
        }
    }
    calculateHours(currentRow);
    validateDate(currentRow.querySelector('.date-field'));
    closeModal();
    updateSummary();
    // Removed database save - this now only updates the frontend row
    // Global "Save" button will handle DB commit for all rows
}


async function loadHistory() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_URL}/timesheets/${loggedInEmployeeId}`, {
            headers: getHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('loggedInEmployeeId');
                window.location.href = 'login.html';
            }
            throw new Error(`Failed to fetch history: ${response.statusText}`);
        }
        const response_json = await response.json();
        console.log('Fetched history data:', response_json); // Debug log
        const historyContent = document.getElementById('historyContent');
        historyContent.innerHTML = '';

        data = response_json.Data;
        if (!data || data.length === 0) {
            historyContent.innerHTML = '<p>No history found</p>';
            return;
        }

        // Group entries by weekPeriod
        let weekMap = new Map();
        data.forEach(entry => {
            const week = entry.weekPeriod;
            if (!weekMap.has(week)) {
                weekMap.set(week, []);
            }
            weekMap.get(week).push(entry);
        });

        for (let [week, weekEntries] of weekMap) {
            let weekDiv = document.createElement('div');
            weekDiv.className = 'history-week-section';
            weekDiv.innerHTML = `<h3>${week}</h3>`;

            let tableWrapper = document.createElement('div');
            tableWrapper.className = 'table-responsive';

            let table = document.createElement('table');
            table.className = 'history-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th class="col-narrow col-sno">S.No</th>
                        <th class="col-narrow col-action">Action</th>
                        <th class="col-medium col-date">Date</th>
                        <th class="col-wide col-location">Location</th>
                        <th class="col-medium col-project-start">Project Start</th>
                        <th class="col-medium col-project-end">Project End</th>
                        <th class="col-medium col-punch-in">Punch In</th>
                        <th class="col-medium col-punch-out">Punch Out</th>
                        <th class="col-wide col-client">Client</th>
                        <th class="col-wide col-project">Project</th>
                        <th class="col-project col-project-code">Project Code</th>
                        <th class="col-wide col-reporting-manager">Reporting Manager</th>
                        <th class="col-wide col-activity">Activity</th>
                        <th class="col-narrow col-project-hours">Project Hours</th>
                        <th class="col-narrow col-working-hours">Working Hours</th>
                        <th class="col-medium col-billable">Billable</th>
                        <th class="col-wide col-remarks">Remarks</th>
                        <th class="col-medium col-created-time">Created Time</th>
                        <th class="col-medium col-updated-time">Updated Time</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            let tbody = table.querySelector('tbody');

            weekEntries.forEach((entry, rowIndex) => {
                const row = document.createElement('tr');
                row.dataset.entryId = entry.id;
                row.innerHTML = `
                    <td class="col-sno">${rowIndex + 1}</td>
                    <td class="col-action"><button class="eye-btn" onclick="openModal(this, true)"><i class="fas fa-eye"></i></button></td>
                    <td class="col-date">${entry.date || ''}</td>
                    <td class="col-location">${entry.location || ''}</td>
                    <td class="col-project-start">${entry.projectStartTime || ''}</td>
                    <td class="col-project-end">${entry.projectEndTime || ''}</td>
                    <td class="col-punch-in">${entry.punchIn || ''}</td>
                    <td class="col-punch-out">${entry.punchOut || ''}</td>
                    <td class="col-client">${entry.client || ''}</td>
                    <td class="col-project">${entry.project || ''}</td>
                    <td class="col-project-code">${entry.projectCode || ''}</td>
                    <td class="col-reporting-manager">${entry.reportingManagerEntry || ''}</td>
                    <td class="col-activity">${entry.activity || ''}</td>
                    <td class="col-project-hours">${entry.hours || ''}</td>
                    <td class="col-working-hours">${entry.workingHours || ''}</td>
                    <td class="col-billable">${entry.billable || ''}</td>
                    <td class="col-remarks">${entry.remarks || ''}</td>
                    <td class="col-created-time">${entry.created_time || ''}</td>
                    <td class="col-updated-time">${entry.updated_time || ''}</td>
                `;
                tbody.appendChild(row);
            });

            tableWrapper.appendChild(table);
            weekDiv.appendChild(tableWrapper);
            historyContent.appendChild(weekDiv);
        }

        // Render feedback only once at the end, using values from the first entry
        const firstEntry = data[0] || {};
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-section';
        feedbackDiv.innerHTML = `
            <div class="feedback-item">
                <label>3 HITS</label>
                <textarea readonly rows="3">${firstEntry.hits || ''}</textarea>
            </div>
            <div class="feedback-item">
                <label>3 MISSES</label>
                <textarea readonly rows="3">${firstEntry.misses || ''}</textarea>
            </div>
            <div class="feedback-item">
                <label>FEEDBACK FOR HR</label>
                <textarea readonly rows="3">${firstEntry.feedback_hr || ''}</textarea>
            </div>
            <div class="feedback-item">
                <label>FEEDBACK FOR IT</label>
                <textarea readonly rows="3">${firstEntry.feedback_it || ''}</textarea>
            </div>
            <div class="feedback-item">
                <label>FEEDBACK FOR CRM</label>
                <textarea readonly rows="3">${firstEntry.feedback_crm || ''}</textarea>
            </div>
            <div class="feedback-item">
                <label>FEEDBACK FOR OTHERS</label>
                <textarea readonly rows="3">${firstEntry.feedback_others || ''}</textarea>
            </div>
        `;
        historyContent.appendChild(feedbackDiv);

        updateAllClientFields();
        updateAllReportingManagerFields();
    } catch (error) {
        console.error('Error loading history:', error); // Debug log
        showPopup(`Failed to load history: ${error.message}`, true);
    }
}