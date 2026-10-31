<script>
  let { title = '', note = '', rows = [], selected = 0, onpick, onhover } = $props()
</script>

<section class="panel">
  {#if note}
    <p class="panel__note">{note}</p>
  {/if}

  <div class="rows">
    {#if rows.length}
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
    {:else}
      <div class="row is-static">
        <span class="row__title">Раздел в работе</span>
        <span class="row__sub">Появится позже</span>
      </div>
    {/if}
  </div>
</section>
