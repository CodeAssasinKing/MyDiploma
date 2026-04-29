// Fakultet Sapaklyk Ulgamy — JavaScript

document.addEventListener('DOMContentLoaded', function () {

  // ── Mobile sidebar toggle ──
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.overlay');
  const menuBtn = document.querySelector('.menu-toggle');

  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('show');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  // ── Active nav link ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
      link.classList.add('active');
    }
  });

  // ── Filter form auto-submit ──
  document.querySelectorAll('.filter-select').forEach(sel => {
    sel.addEventListener('change', () => {
      sel.closest('form').submit();
    });
  });

  // ── Print button ──
  const printBtn = document.getElementById('btn-print');
  if (printBtn) {
    printBtn.addEventListener('click', () => window.print());
  }

  // ── Lesson card tooltip on hover (simple) ──
  document.querySelectorAll('.lesson-card').forEach(card => {
    card.setAttribute('title', card.querySelector('.lesson-name')?.textContent?.trim() || '');
  });

  // ── Scroll to today's day block ──
  const today = new Date().getDay(); // 0=Sun,1=Mon,...
  const dayMap = { 1: 'MON', 2: 'TUE', 3: 'WED', 4: 'THU', 5: 'FRI', 6: 'SAT', 0: 'SUN' };
  const todayCode = dayMap[today];
  const todayRow = document.querySelector(`[data-day="${todayCode}"]`);
  if (todayRow) {
    todayRow.classList.add('today-highlight');
    setTimeout(() => {
      todayRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 300);
  }

  // ── Group filter checkboxes (if present) ──
  const groupFilterBtns = document.querySelectorAll('.group-filter-btn');
  groupFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const groupId = btn.dataset.groupId;
      const cols = document.querySelectorAll(`[data-group-id="${groupId}"]`);
      const isHidden = btn.classList.toggle('hidden-group');
      cols.forEach(col => {
        col.style.display = isHidden ? 'none' : '';
      });
    });
  });

  // ── Sticky header shadow on scroll ──
  const header = document.querySelector('.top-header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.style.boxShadow = window.scrollY > 5
        ? '0 4px 16px rgba(0,0,0,0.12)'
        : '0 2px 8px rgba(0,0,0,0.05)';
    });
  }
});

// ── Utility: highlight searched text in teacher/classroom selects ──
function filterSelect(inputId, selectId) {
  const input = document.getElementById(inputId);
  const select = document.getElementById(selectId);
  if (!input || !select) return;
  const options = Array.from(select.options);
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    options.forEach(opt => {
      opt.style.display = opt.text.toLowerCase().includes(q) ? '' : 'none';
    });
  });
}
