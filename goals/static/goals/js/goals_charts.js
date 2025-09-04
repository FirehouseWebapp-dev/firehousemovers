(function(){
  function renderSingleDonut(canvasId, value, total, color) {
    var el = document.getElementById(canvasId);
    if (!el || typeof Chart === 'undefined') return null;
    var count = parseInt(value || '0', 10);
    var denom = parseInt(total || '0', 10);
    if (!Number.isFinite(denom) || denom < 1) denom = 1;
    var remain = Math.max(denom - count, 0);

    return new Chart(el, {
      type: 'doughnut',
      data: {
        labels: [],
        datasets: [{
          data: [count, remain],
          backgroundColor: [color, '#374151'],
          borderWidth: 0,
          cutout: '80%'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      }
    });
  }

  function initCharts() {
    if (typeof Chart === 'undefined') return;
    var completedEl = document.getElementById('chartCompleted');
    var pendingEl = document.getElementById('chartPending');
    var shortEl = document.getElementById('chartShort');
    var longEl = document.getElementById('chartLong');

    var completedChart = renderSingleDonut('chartCompleted', completedEl && completedEl.dataset.value, completedEl && completedEl.dataset.total, '#22c55e');
    var pendingChart = renderSingleDonut('chartPending', pendingEl && pendingEl.dataset.value, pendingEl && pendingEl.dataset.total, '#ef4444');
    var shortChart = renderSingleDonut('chartShort', shortEl && shortEl.dataset.value, shortEl && shortEl.dataset.total, '#3b82f6');
    var longChart = renderSingleDonut('chartLong', longEl && longEl.dataset.value, longEl && longEl.dataset.total, '#f59e0b');

    window.GoalsCharts = {
      completed: completedChart,
      pending: pendingChart,
      short: shortChart,
      long: longChart,
      updateAll: function(counts) {
        try {
          var total = Math.max(parseInt(counts.total || '0', 10), 1);
          var sets = [
            { chart: this.completed, val: parseInt(counts.completed || '0', 10) },
            { chart: this.pending, val: parseInt(counts.pending || '0', 10) },
            { chart: this.short, val: parseInt(counts.short_term || '0', 10) },
            { chart: this.long, val: parseInt(counts.long_term || '0', 10) }
          ];
          sets.forEach(function(s){
            if (!s.chart) return;
            s.chart.data.datasets[0].data = [Math.max(0, s.val), Math.max(0, total - s.val)];
            s.chart.update('none');
          });
        } catch (e) { 
          // Chart update error - fail silently to not disrupt user experience
        }
      }
    };
  }

  document.addEventListener('DOMContentLoaded', initCharts);
})();
