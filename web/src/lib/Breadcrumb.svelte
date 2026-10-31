<script>
  let { items = [] } = $props()
</script>

<nav class="crumbs" aria-label="Путь">
  {#each items as item, i}
    {#if i > 0}
      <span class="crumbs__sep" aria-hidden="true"></span>
    {/if}
    <span class="crumbs__item" class:is-current={i === items.length - 1}>{item}</span>
  {/each}
</nav>
