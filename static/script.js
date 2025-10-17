document.addEventListener('DOMContentLoaded', function() {

    // Responsive behavior
    window.addEventListener('resize', function() {
      const sidebar = document.querySelector('.sidebar');
      const overlay = document.querySelector('.overlay');

      if (window.innerWidth > 768) {
        if (sidebar) sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
});
