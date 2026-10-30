<script>
  import Glyph from './Glyph.svelte'

  let {
    tiles = [],
    selected = 0,
    active = true,
    enter = 0,
    cols = 4,
    rows = 2,
    onpick,
    onhover,
  } = $props()

  function shift(tile) {
    const cx = tile.col + tile.colSpan / 2 - 0.5
    const cy = tile.row + tile.rowSpan / 2 - 0.5
    const x = cx < (cols + 1) / 2 ? -6 : 6
    const y = cy <= (rows + 1) / 2 ? -6 : 6
    return { x, y }
  }

  function glyphSize(tile) {
    if (tile.rowSpan === 2) return 152
    if (tile.colSpan === 2) return 120
    return 76
  }
</script>

<section class="grid" class:is-entering={enter !== 0} style="--enter: {enter}">
  {#each tiles as tile, i}
    {@const push = shift(tile)}
    <button
      class="tile"
      class:is-selected={active && i === selected}
      class:tile--hero={tile.rowSpan === 2}
      class:tile--wide={tile.rowSpan === 1 && tile.colSpan === 2}
      style="grid-column: {tile.col} / span {tile.colSpan}; grid-row: {tile.row} / span {tile.rowSpan}; --push-x: {push.x}px; --push-y: {push.y}px; --i: {i};"
      onpointerenter={() => onhover?.(i)}
      onclick={() => onpick?.(i)}
    >
      <span class="tile__title">{tile.title}</span>
      {#if tile.sub}
        <span class="tile__sub">{tile.sub}</span>
      {/if}

      {#if tile.match || tile.tags || tile.glyph}
        <span class="tile__meta">
          {#if tile.match}
            <span class="tile__match">
              {tile.match.label}
              <b>{tile.match.value}</b>
            </span>
          {:else if tile.tags}
            <span class="tile__tags">{tile.tags.join(' · ')}</span>
          {/if}
          {#if tile.glyph}
            <span class="tile__glyph">
              <Glyph name={tile.glyph} size={glyphSize(tile)} />
            </span>
          {/if}
        </span>
      {/if}
    </button>
  {/each}
</section>
