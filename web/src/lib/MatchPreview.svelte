<script>
  let { home, away } = $props()

  const homeLine = [
    { x: 48, y: 150 },
    { x: 100, y: 58 },
    { x: 100, y: 118 },
    { x: 100, y: 182 },
    { x: 100, y: 242 },
    { x: 158, y: 82 },
    { x: 158, y: 150 },
    { x: 158, y: 218 },
    { x: 236, y: 64 },
    { x: 246, y: 150 },
    { x: 236, y: 236 },
  ]

  const awayLine = homeLine.map((point) => ({ x: 420 - point.x, y: point.y }))
</script>

<svg class="pitch" viewBox="0 0 420 300" aria-hidden="true">
  <rect width="420" height="300" fill="#1f7a44" />
  {#each Array.from({ length: 7 }, (_, index) => index * 60) as x (x)}
    <rect x={x} width="30" height="300" fill="#1c6e3d" />
  {/each}

  <g class="pitch__lines">
    <rect x="16" y="14" width="388" height="272" />
    <path d="M210 14V286" />
    <circle cx="210" cy="150" r="34" />
    <rect x="16" y="78" width="52" height="144" />
    <rect x="16" y="116" width="20" height="68" />
    <rect x="352" y="78" width="52" height="144" />
    <rect x="384" y="116" width="20" height="68" />
    <path d="M72 128V172M348 128V172" />
  </g>

  <g class="pitch__ball">
    <circle cx="210" cy="150" r="3.4" />
  </g>

  {#each homeLine as player, index (index)}
    <g class="pitch__player" transform={`translate(${player.x} ${player.y})`}>
      <circle cy="-7" r="3" class="pitch__head" />
      <rect x="-4.5" y="-5.5" width="9" height="10" fill={home?.shirt ?? '#f5f7fa'} />
    </g>
  {/each}

  {#each awayLine as player, index (index)}
    <g class="pitch__player" transform={`translate(${player.x} ${player.y})`}>
      <circle cy="-7" r="3" class="pitch__head" />
      <rect x="-4.5" y="-5.5" width="9" height="10" fill={away?.shirt ?? '#f5f7fa'} />
    </g>
  {/each}
</svg>

<style>
  .pitch {
    display: block;
    width: 100%;
    height: 100%;
  }

  .pitch__lines {
    fill: none;
    stroke: rgba(255, 255, 255, 0.8);
    stroke-width: 2;
  }

  .pitch__ball circle {
    fill: #f6f8fb;
    filter: drop-shadow(0 1px 1px rgba(4, 9, 20, 0.45));
  }

  .pitch__player {
    filter: drop-shadow(0 1px 1.5px rgba(4, 9, 20, 0.4));
  }

  .pitch__head {
    fill: #e2bf9c;
  }
</style>
