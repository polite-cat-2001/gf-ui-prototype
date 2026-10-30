<script>
  let { title = '', note = '', rows = [], selected = 0, onpick, onhover } = $props()
</script>

<section class="panel">
  <header class="panel__head">
    <p class="panel__eyebrow">Раздел</p>
    <h2 class="panel__title">{title}</h2>
    {#if note}<p class="panel__note">{note}</p>{/if}
  </header>

  {#if rows.length}
    <div class="rows">
      {#each rows as row, i}
        <button
          class="row"
          class:is-selected={i === selected}
          onpointerenter={() => onhover?.(i)}
          onclick={() => onpick?.(i)}
        >
          <span class="row__title">{row.title}</span>
          {#if row.sub}<span class="row__sub">{row.sub}</span>{/if}
        </button>
      {/each}
    </div>
  {/if}
</section>
