<script>
  import { onMount } from 'svelte'
  import Glyph from './Glyph.svelte'
  import { loadClubs, loadCountries, loadLeagues, loadNationalTeams, loadRatings, topLeague } from './teams.js'

  let { devices = [], onback, onready } = $props()

  const FOCUS_ORDER = ['country', 'club', 'league']
  const NATIONAL_COUNTRY = { id: 'national', name: 'National teams', flag: null }
  const NATIONAL_LEAGUE = { id: 'national-men', name: 'National teams (men)', logo: null }

  let countries = $state([])
  let sides = $state([createSide('home'), createSide('away')])
  let activeSide = $state('home')
  let error = $state('')

  const homeDevices = $derived(devices.filter((device) => device.connected && device.side === 'home'))
  const awayDevices = $derived(devices.filter((device) => device.connected && device.side === 'away'))
  const parallel = $derived(homeDevices.length > 0 && awayDevices.length > 0)

  function createSide(id) {
    return {
      id,
      focus: 'club',
      ready: false,
      seq: 0,
      countryIndex: 0,
      leagueIndex: 0,
      clubIndex: 0,
      leagues: [],
      clubs: [],
      ratings: {},
    }
  }

  const sideOf = (id) => sides.find((side) => side.id === id)
  const isLive = (side) => !side.ready && (parallel || side.id === activeSide)

  async function syncClubs(side, token) {
    const league = side.leagues[side.leagueIndex]
    if (!league) return
    const [clubs, ratings] = await Promise.all([loadClubs(league.id), loadRatings(league.id)])
    if (token !== side.seq) return
    side.clubs = clubs
    side.ratings = ratings
    side.clubIndex = 0
  }

  async function changeCountry(side, step) {
    if (countries.length < 2) return
    const token = ++side.seq
    side.countryIndex = (side.countryIndex + step + countries.length) % countries.length
    side.leagueIndex = 0
    side.clubIndex = 0
    side.leagues = []
    side.clubs = []
    const country = countries[side.countryIndex]

    if (country.id === 'national') {
      const teams = await loadNationalTeams()
      if (token !== side.seq) return
      side.leagues = [NATIONAL_LEAGUE]
      side.clubs = teams.map((team) => ({ id: team.id, name: team.name, logo: team.emblem ?? team.flag }))
      side.ratings = Object.fromEntries(teams.map((team) => [team.id, team]))
      return
    }

    const leagues = await loadLeagues(country.id)
    if (token !== side.seq) return
    side.leagues = leagues
    side.leagueIndex = Math.max(0, leagues.indexOf(topLeague(leagues)))
    await syncClubs(side, token)
  }

  async function changeLeague(side, step) {
    if (side.leagues.length < 2) return
    const token = ++side.seq
    side.leagueIndex = (side.leagueIndex + step + side.leagues.length) % side.leagues.length
    side.clubIndex = 0
    side.clubs = []
    await syncClubs(side, token)
  }

  function changeClub(side, step) {
    if (side.clubs.length < 2) return
    side.clubIndex = (side.clubIndex + step + side.clubs.length) % side.clubs.length
  }

  function confirm(side) {
    side.ready = true
    if (parallel) {
      if (sideOf('home').ready && sideOf('away').ready) onready?.()
      return
    }
    if (side.id === 'home') {
      activeSide = 'away'
      sideOf('away').focus = 'club'
    } else {
      onready?.()
    }
  }

  function back() {
    if (!parallel) {
      const home = sideOf('home')
      if (activeSide === 'away' && home.ready) {
        home.ready = false
        home.focus = 'club'
        activeSide = 'home'
        return
      }
    }
    onback?.()
  }

  function sideForDevice(deviceId) {
    if (!parallel) return sideOf(activeSide)
    const device = devices.find((item) => item.id === deviceId)
    if (!device) return null
    return device.side === 'home' || device.side === 'away' ? sideOf(device.side) : null
  }

  export function input(deviceId, action) {
    if (action === 'back') {
      back()
      return
    }

    const side = sideForDevice(deviceId)
    if (!side || !isLive(side)) return

    if (action === 'confirm') {
      confirm(side)
      return
    }

    if (action === 'up' || action === 'down') {
      const index = FOCUS_ORDER.indexOf(side.focus)
      side.focus = FOCUS_ORDER[Math.min(FOCUS_ORDER.length - 1, Math.max(0, index + (action === 'up' ? -1 : 1)))]
      return
    }

    const step = action === 'left' ? -1 : action === 'right' ? 1 : 0
    if (!step) return

    if (side.focus === 'country') changeCountry(side, step)
    else if (side.focus === 'league') changeLeague(side, step)
    else changeClub(side, step)
  }

  onMount(async () => {
    try {
      countries = [NATIONAL_COUNTRY, ...(await loadCountries())]
      const spain = countries.find((country) => country.name === 'Spain') ?? countries[0]
      const leagues = await loadLeagues(spain.id)
      const league = topLeague(leagues)
      const [clubs, ratings] = await Promise.all([loadClubs(league.id), loadRatings(league.id)])

      sides = sides.map((side) => ({
        ...side,
        countryIndex: countries.indexOf(spain),
        leagues,
        leagueIndex: Math.max(0, leagues.indexOf(league)),
        clubs,
        ratings,
      }))

      const barcelona = clubs.findIndex((club) => club.name === 'FC Barcelona')
      const madrid = clubs.findIndex((club) => club.name === 'Real Madrid')
      sideOf('home').clubIndex = Math.max(0, barcelona)
      sideOf('away').clubIndex = Math.max(0, madrid)
    } catch (caught) {
      error = caught.message
    }
  })
</script>

<div class="teams">
  {#each sides as side (side.id)}
    {@const country = countries[side.countryIndex]}
    {@const league = side.leagues[side.leagueIndex]}
    {@const club = side.clubs[side.clubIndex]}
    {@const rating = club ? side.ratings[club.id] : null}
    {@const stars = rating?.stars ?? 0}
    {@const live = isLive(side)}
    <article class="team" class:is-idle={!live && !side.ready} class:is-ready={side.ready}>
      {#if side.ready}
        <div class="team__block team__block--mark">
          <span class="team__mark">{side.id === 'home' ? 'Дома' : 'Гости'}</span>
        </div>
      {:else}
        <div class="team__block team__block--country" class:is-focus={live && side.focus === 'country'}>
          <span class="team__name team__name--country">{country?.name ?? ''}</span>
          <div class="team__art">
            {#if country?.id === 'national'}
              <span class="team__globe"><Glyph name="globe" size={52} /></span>
            {:else if country}
              <img class="team__flag" src={country.flag} alt="" />
            {/if}
            {#if live && side.focus === 'country' && countries.length > 1}
              <span class="team__cue team__cue--left"></span>
              <span class="team__cue team__cue--right"></span>
            {/if}
          </div>
        </div>
      {/if}

      <div class="team__block team__block--club" class:is-focus={live && side.focus === 'club'}>
        <span class="team__name team__name--club">{club?.name ?? '—'}</span>
        <div class="team__art team__art--crest">
          {#if club}<img class="team__crest" src={club.logo} alt="" />{/if}
          {#if live && side.focus === 'club' && side.clubs.length > 1}
            <span class="team__cue team__cue--left"></span>
            <span class="team__cue team__cue--right"></span>
          {/if}
        </div>
        <span class="team__stars">
          {#each Array.from({ length: 5 }, (_, index) => index) as index (index)}
            <span
              class="team__star"
              class:team__star--full={stars >= index + 1}
              class:team__star--half={stars > index && stars < index + 1}
            >★</span>
          {/each}
        </span>
        <div class="team__stats">
          <span class="team__stat"><em>Нап</em><b>{rating?.attack ?? '—'}</b></span>
          <span class="team__stat"><em>Пзщ</em><b>{rating?.midfield ?? '—'}</b></span>
          <span class="team__stat"><em>Защ</em><b>{rating?.defence ?? '—'}</b></span>
        </div>
      </div>

      {#if side.ready}
        <div class="team__block team__block--mark">
          <span class="team__mark team__mark--ready">Готов!</span>
        </div>
      {:else}
        <div class="team__block team__block--league" class:is-focus={live && side.focus === 'league'}>
          <span class="team__name team__name--league">{league?.name ?? ''}</span>
          <div class="team__art">
            {#if league?.logo}
              <img class="team__league" src={league.logo} alt="" />
            {:else if league}
              <span class="team__globe"><Glyph name="shirt" size={52} /></span>
            {/if}
            {#if live && side.focus === 'league' && side.leagues.length > 1}
              <span class="team__cue team__cue--left"></span>
              <span class="team__cue team__cue--right"></span>
            {/if}
          </div>
        </div>
      {/if}
    </article>
  {/each}
</div>

{#if error}
  <p class="teams__error">API недоступен: {error}</p>
{/if}
