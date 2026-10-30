<script>
  let { meta } = $props()
</script>

<section class="panel">
  <p class="eyebrow">Экран</p>
  <h2>Составы</h2>
  <p>
    Здесь будет поле со слотами, панель фокуса игрока, запасные и резерв, обмен игроков A/B — по
    тем же золотым правилам, что в карьерном прототипе. Лица и формы уже в статике.
  </p>
  <div class="facts">
    <span class="fact">игроков в каноне: {meta?.counts?.players ?? '—'}</span>
  </div>
</section>
