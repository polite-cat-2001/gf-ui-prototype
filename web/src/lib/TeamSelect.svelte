<script>
  let { meta } = $props()
</script>

<section class="panel">
  <p class="eyebrow">Экран</p>
  <h2>Выбор команды</h2>
  <p>
    Здесь будет выбор страны, лиги и клуба по Figma: крупный центральный объект и панель деталей,
    переход A/B. Канон уже подключён к API.
  </p>
  <div class="facts">
    <span class="fact">стран: {meta?.counts?.countries ?? '—'}</span>
    <span class="fact">лиг: {meta?.counts?.leagues ?? '—'}</span>
    <span class="fact">клубов: {meta?.counts?.clubs ?? '—'}</span>
    <span class="fact">игроков: {meta?.counts?.players ?? '—'}</span>
  </div>
</section>
