<script>
  let { onplay, onlineup } = $props()
</script>

<section class="menu">
  <p class="eyebrow">GameplayFootball</p>
  <h1>UI Prototype</h1>
  <div class="menu-actions">
    <button class="menu-button" data-nav data-autofocus onclick={onplay}>
      Играть
      <span>Выбор команды</span>
    </button>
    <button class="menu-button" data-nav onclick={onlineup}>
      Составы
      <span>Стартовый состав и схема</span>
    </button>
    <button class="menu-button" data-nav disabled>
      Настройки
      <span>скоро</span>
    </button>
  </div>
</section>
