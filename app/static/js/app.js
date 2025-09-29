// app/static/js/app.js
function updateData() {
  console.log("Updating data from backend...");
  fetch("/update")
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Data updated successfully");
        showNotification("Data berhasil diperbarui!", "success");
        // Refresh UI immediately instead of reload
        refreshUI();
      } else {
        console.error("Update failed:", data.error);
        showNotification("Error: " + data.error, "error");
      }
    })
    .catch((error) => {
      console.error("Update error:", error);
      showNotification("Error: " + error, "error");
    });
}

function refreshUI() {
  console.log("Refreshing UI...");
  fetch("/api/status")
    .then((response) => response.json())
    .then((data) => {
      const now = new Date().toLocaleString('id-ID', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      });

      // Update last updated time
      document.getElementById("last-updated").textContent = `Terakhir Diperbarui: ${now}`;

      // Update device info
      const deviceInfo = data.device_info;
      if (deviceInfo) {
        document.getElementById("device-id").textContent = deviceInfo.device_id || 'N/A';
        document.getElementById("product-name").textContent = deviceInfo.product_name || 'N/A';
        document.getElementById("ip-address").textContent = deviceInfo.ip_address || 'N/A';
        const statusEl = document.getElementById("online-status");
        statusEl.textContent = deviceInfo.online_status || 'Unknown';
        statusEl.className = deviceInfo.online_status === 'Online' ? 'badge bg-success' : 'badge bg-danger';
        document.getElementById("device-last-updated").textContent = new Date(deviceInfo.last_updated).toLocaleString('id-ID');
        document.getElementById("device-info-fallback").style.display = 'none';
      } else {
        document.getElementById("device-info-fallback").style.display = 'block';
      }

      // Update switches
      const switchesContainer = document.getElementById("switches-container");
      const currentSwitches = data.current_switches;
      if (currentSwitches && currentSwitches.length > 0) {
        switchesContainer.innerHTML = '';
        currentSwitches.forEach(switch => {
          const colDiv = document.createElement('div');
          colDiv.className = 'col-6 mb-3 switch-item';
          colDiv.setAttribute('data-switch', switch.switch_name);
          colDiv.innerHTML = `
            <div class="text-center">
              <div class="fw-bold">${switch.switch_name}</div>
              <div class="switch-status mt-2">
                <span class="badge ${switch.status ? 'bg-success' : 'bg-danger'}">${switch.status ? 'ON' : 'OFF'}</span>
              </div>
            </div>
          `;
          switchesContainer.appendChild(colDiv);
        });
        document.getElementById("switches-fallback").style.display = 'none';
      } else {
        switchesContainer.innerHTML = '<div class="col-12"><p class="text-muted text-center" id="switches-fallback">Data switch belum tersedia</p></div>';
      }

      // Update logs (limit to 10 recent)
      const logsBody = document.getElementById("logs-body");
      const recentLogs = data.recent_logs.slice(0, 10);
      if (recentLogs && recentLogs.length > 0) {
        logsBody.innerHTML = '';
        recentLogs.forEach(log => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${new Date(log.created_at).toLocaleString('id-ID')}</td>
            <td>${log.switch_name}</td>
            <td><span class="badge ${log.status ? 'bg-success' : 'bg-danger'}">${log.status ? 'ON' : 'OFF'}</span></td>
          `;
          logsBody.appendChild(row);
        });
      } else {
        logsBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Belum ada riwayat status</td></tr>';
      }

      console.log("UI refreshed successfully");
    })
    .catch((error) => {
      console.error("UI refresh error:", error);
      showNotification("Error refreshing UI: " + error, "error");
    });
}

function showNotification(message, type) {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = `alert alert-${
    type === "success" ? "success" : "danger"
  } alert-dismissible fade show`;
  notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.zIndex = "9999";
  notification.style.minWidth = "300px";

  document.body.appendChild(notification);

  // Auto remove after 3 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 3000);
}

// Auto-update every 30 seconds
setInterval(updateData, 30000);

// Auto-refresh UI every 10 seconds
setInterval(refreshUI, 10000);

// Initial UI refresh on load
document.addEventListener("DOMContentLoaded", function () {
  console.log("Bardi Monitoring initialized");
  refreshUI(); // Initial load
});

// Manual update function
window.updateDataManual = function () {
  const btn = document.querySelector(".btn-primary");
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';

  updateData();

  // Re-enable button after update completes
  setTimeout(() => {
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-refresh me-2"></i>Update Data Sekarang';
  }, 3000); // Give time for backend update
};
