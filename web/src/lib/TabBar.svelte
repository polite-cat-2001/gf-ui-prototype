<script>
  import { onMount } from 'svelte'

  let { tabs = [], index = 0, focused = false, onselect } = $props()

  let bar = $state(null)
  let left = $state(0)
  let width = $state(0)
  let ready = $state(false)

  function measure() {
    if (!bar) return
    const el = bar.querySelectorAll('.tab')[index]
    if (!el) return
    left = el.offsetLeft
    width = el.offsetWidth
    ready = true
  }

  $effect(() => {
    index
    bar
    measure()
  })

  onMount(() => {
    document.fonts?.ready.then(() => measure())
    const onResize = () => measure()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  })
</script>

<nav
  class="tabbar"
  class:is-ready={ready}
  class:is-focused={focused}
  bind:this={bar}
  aria-label="Разделы"
>
  <span class="tabbar__marker" style="transform: translateX({left}px); width: {width}px;"></span>
  {#each tabs as item, i}
    <button class="tab" class:is-active={i === index} onclick={() => onselect?.(i, 'click')}>
      {item.label}
    </button>
  {/each}
</nav>
