<script>
  import { onMount } from 'svelte'
  import { api } from './lib/api.js'
  import Controls from './lib/Controls.svelte'
  import MainMenu from './lib/MainMenu.svelte'
  import TeamSelect from './lib/TeamSelect.svelte'
  import Lineup from './lib/Lineup.svelte'

  let screen = $state('menu')
  let meta = $state(null)
  let error = $state('')

  let hints = $derived(
    screen === 'menu'
      ? [
          { keys: ['Enter'], label: 'Выбрать' },
          { keys: ['Esc'], label: 'Выход' },
        ]
      : [{ keys: ['Esc'], label: 'Назад' }],
  )

  onMount(async () => {
    try {
      meta = await api.meta()
    } catch (caught) {
      error = caught.message
    }
  })

  function handleKeydown(event) {
    if (event.key === 'Escape' && screen !== 'menu') {
      event.preventDefault()
      screen = 'menu'
    }
  }

  function openTeamSelect() {
    screen = 'team-select'
  }

  function openLineup() {
    screen = 'lineup'
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="app">
  <header class="topbar">
    <div class="brand">GF <span>UI</span></div>
    <div class="status" class:ok={meta} class:error={error}>
      {#if error}
        API недоступен: {error}
      {:else if meta}
        канон: {meta.counts.clubs} клубов · {meta.counts.players} игроков
      {:else}
        подключение к API…
      {/if}
    </div>
  </header>

  <main class="screen">
    {#if screen === 'menu'}
      <MainMenu onplay={openTeamSelect} onlineup={openLineup} />
    {:else if screen === 'team-select'}
      <TeamSelect {meta} />
    {:else if screen === 'lineup'}
      <Lineup {meta} />
    {/if}
  </main>

  <Controls {hints} />
</div>
