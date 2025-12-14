// filename: static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
  // Auto-dismiss alerts after 5 seconds
  setTimeout(() => {
      const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
      alerts.forEach(alert => {
          const bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
      });
  }, 5000);
  
  // Form validation enhancements
  const forms = document.querySelectorAll('.needs-validation');
  forms.forEach(form => {
      form.addEventListener('submit', function(event) {
          if (!form.checkValidity()) {
              event.preventDefault();
              event.stopPropagation();
          }
          form.classList.add('was-validated');
      }, false);
  });
  
  // Tooltip initialization
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Popover initialization
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function(popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
  });
  
  // Auto-focus first input in forms
  const firstInput = document.querySelector('form input[type="text"], form input[type="email"], form input[type="password"]');
  if (firstInput && !firstInput.value) {
      firstInput.focus();
  }
  
  // Deadline urgency coloring
  function updateDeadlineColors() {
      const deadlineCells = document.querySelectorAll('[data-deadline]');
      deadlineCells.forEach(cell => {
          const days = parseInt(cell.dataset.deadline);
          if (!isNaN(days)) {
              if (days < 0) {
                  cell.classList.add('text-danger', 'fw-bold');
              } else if (days <= 3) {
                  cell.classList.add('text-danger');
              } else if (days <= 7) {
                  cell.classList.add('text-warning');
              }
          }
      });
  }
  
  updateDeadlineColors();
  
  // Status update confirmation
  const statusForms = document.querySelectorAll('.status-update-form');
  statusForms.forEach(form => {
      form.addEventListener('submit', function(e) {
          const newStatus = this.querySelector('select').value;
          const currentStatus = this.dataset.currentStatus;
          
          if (newStatus === currentStatus) {
              e.preventDefault();
              return false;
          }
          
          if (newStatus === 'Rejected' || newStatus === 'Withdrawn') {
              if (!confirm('Are you sure you want to mark this application as ' + newStatus + '?')) {
                  e.preventDefault();
                  return false;
              }
          }
      });
  });
  
  // Copy to clipboard functionality
  const copyButtons = document.querySelectorAll('.btn-copy');
  copyButtons.forEach(button => {
      button.addEventListener('click', function() {
          const textToCopy = this.dataset.copy;
          navigator.clipboard.writeText(textToCopy).then(() => {
              const originalHTML = this.innerHTML;
              this.innerHTML = '<i class="fas fa-check"></i> Copied!';
              this.classList.remove('btn-outline-secondary');
              this.classList.add('btn-success');
              
              setTimeout(() => {
                  this.innerHTML = originalHTML;
                  this.classList.remove('btn-success');
                  this.classList.add('btn-outline-secondary');
              }, 2000);
          });
      });
  });
  
  // Dark mode toggle
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle) {
      darkModeToggle.addEventListener('click', function() {
          const html = document.documentElement;
          const isDark = html.getAttribute('data-bs-theme') === 'dark';
          
          if (isDark) {
              html.setAttribute('data-bs-theme', 'light');
              localStorage.setItem('theme', 'light');
              this.innerHTML = '<i class="fas fa-moon"></i>';
          } else {
              html.setAttribute('data-bs-theme', 'dark');
              localStorage.setItem('theme', 'dark');
              this.innerHTML = '<i class="fas fa-sun"></i>';
          }
      });
      
      // Load saved theme
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) {
          document.documentElement.setAttribute('data-bs-theme', savedTheme);
          darkModeToggle.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
      }
  }
  
  // Application status quick update
  document.querySelectorAll('.quick-status-btn').forEach(btn => {
      btn.addEventListener('click', function() {
          const applicationId = this.dataset.applicationId;
          const newStatus = this.dataset.status;
          
          fetch(`/applications/${applicationId}/quick-status`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': document.querySelector('[name="csrf_token"]').value
              },
              body: JSON.stringify({ status: newStatus })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  // Update the status badge
                  const statusBadge = document.querySelector(`#status-badge-${applicationId}`);
                  if (statusBadge) {
                      statusBadge.textContent = newStatus;
                      statusBadge.className = `badge bg-${data.status_color}`;
                  }
                  
                  // Show success message
                  const alert = document.createElement('div');
                  alert.className = 'alert alert-success alert-dismissible fade show';
                  alert.innerHTML = `
                      Status updated to ${newStatus}
                      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                  `;
                  document.querySelector('.container.py-4').prepend(alert);
              }
          });
      });
  });
  
  // Search with debounce
  let searchTimeout;
  const searchInput = document.getElementById('globalSearch');
  if (searchInput) {
      searchInput.addEventListener('input', function() {
          clearTimeout(searchTimeout);
          searchTimeout = setTimeout(() => {
              this.form.submit();
          }, 500);
      });
  }
  
  // Initialize all charts if Chart.js is loaded
  if (typeof Chart !== 'undefined') {
      initializeCharts();
  }
});

function initializeCharts() {
  // This function would initialize Chart.js charts if needed
  // Currently left as a placeholder for future enhancement
}