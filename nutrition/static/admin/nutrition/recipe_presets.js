(function() {
  function onReady() {
    const el = document.getElementById('yield-presets-json');
    const PRESETS = JSON.parse(el?.textContent || '{}');
    console.log("PRESETS 로드됨:", PRESETS);

    const cat = document.getElementById('id_category');
    const yieldInput = document.getElementById('id_yield_rate');
    if (!cat || !yieldInput) return;

    // 페이지 로드시 기본값 세팅
    if (cat.value && PRESETS[cat.value]) {
      yieldInput.value = PRESETS[cat.value];
    }

    // 카테고리 바뀔 때마다 세팅
    cat.addEventListener('change', () => {
      const key = cat.value.trim();
      const v = PRESETS[key];
      console.log("선택된 값:", key, "→ preset:", v);
      if (v !== undefined) {
        yieldInput.value = v;
      }
    });
  }

  if (document.readyState !== 'loading') onReady();
  else document.addEventListener('DOMContentLoaded', onReady);
})();
