window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    resizeMapOnTab: function(activeTab) {
      if (activeTab === "runoff-calculator") {
        // Defer to next tick so the tab is fully visible before resizing
        setTimeout(function() {
          try {
            window.dispatchEvent(new Event("resize"));
          } catch (e) {
            // Fallback for older browsers
            var evt = document.createEvent("UIEvents");
            evt.initUIEvent("resize", true, false, window, 0);
            window.dispatchEvent(evt);
          }
        }, 0);
      }
      return window.dash_clientside.no_update;
    },

    initOverviewTooltips: function() {
      // Initialize Bootstrap tooltips for overview tab elements
      initOverviewTooltips(); // Immediately initialize tooltips when dashboard loads
      return window.dash_clientside.no_update;
    }
  }
});


