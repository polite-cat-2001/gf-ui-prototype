<script module>
  let seq = 0
</script>

<script>
  let { kit } = $props()

  const uid = `kit-art-${++seq}`
  const shirt = 'M80 10 58 18 26 32 8 76 50 94 66 74V186H174V74L190 94 232 76 214 32 182 18 160 10C148 26 135 32 120 32S92 26 80 10Z'
  const collar = 'M80 10C92 26 105 32 120 32S148 26 160 10'

  const pattern = $derived(kit?.pattern ?? 'plain')
  const accent = $derived(kit?.pattern_color ?? '#000000')
  const stripes = $derived(Array.from({ length: 8 }, (_, index) => -44 + index * 44))
  const hoops = $derived(Array.from({ length: 6 }, (_, index) => index * 34))
</script>

<svg class="kitart" viewBox="0 0 240 196" aria-hidden="true">
  <defs>
    <clipPath id={`${uid}-shirt`}>
      <path d={shirt} />
    </clipPath>
  </defs>

  <path d={shirt} fill={kit?.shirt ?? '#f5f7fa'} />
  <g clip-path={`url(#${uid}-shirt)`}>
    {#if pattern === 'stripes'}
      {#each stripes as x (x)}
        <rect x={x} y="0" width="22" height="200" fill={accent} />
      {/each}
    {:else if pattern === 'halves'}
      <rect x="0" y="0" width="120" height="200" fill={accent} />
    {:else if pattern === 'hoops'}
      {#each hoops as y (y)}
        <rect x="0" y={y} width="240" height="17" fill={accent} />
      {/each}
    {:else if pattern === 'sash'}
      <rect
        x="-90"
        y="86"
        width="420"
        height="38"
        fill={accent}
        transform="rotate(-34 120 120)"
      />
    {/if}
  </g>
  <path class="kitart__edge" d={shirt} />
  <g clip-path={`url(#${uid}-shirt)`}>
    <path class="kitart__collar" d={collar} stroke={kit?.shorts ?? '#f5f7fa'} />
  </g>
</svg>

<style>
  .kitart {
    display: block;
    width: 100%;
    height: 100%;
    overflow: visible;
    filter: drop-shadow(0 14px 20px rgba(4, 9, 20, 0.22));
  }

  .kitart__edge {
    fill: none;
    stroke: rgba(23, 27, 63, 0.26);
    stroke-width: 1.4;
  }

  .kitart__collar {
    fill: none;
    stroke-width: 7;
    stroke-linecap: butt;
    opacity: 0.92;
  }
</style>
