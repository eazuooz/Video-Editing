mergeInto(LibraryManager.library, {
  LofiReportState: function (state) {
    window.dispatchEvent(new CustomEvent('lofi-state', {detail:JSON.parse(UTF8ToString(state))}));
  }
});
