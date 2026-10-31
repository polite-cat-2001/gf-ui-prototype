import { api } from './api.js'

const leagueCache = new Map()
const clubCache = new Map()
const ratingCache = new Map()

let countriesPromise
let nationalPromise

export function loadCountries() {
  countriesPromise ??= api.countries()
  return countriesPromise
}

export function loadNationalTeams() {
  nationalPromise ??= api.nationalTeams()
  return nationalPromise
}

export function loadLeagues(countryId) {
  if (!leagueCache.has(countryId)) leagueCache.set(countryId, api.leagues(countryId))
  return leagueCache.get(countryId)
}

export function loadClubs(leagueId) {
  if (!clubCache.has(leagueId)) clubCache.set(leagueId, api.clubs(leagueId))
  return clubCache.get(leagueId)
}

export function loadRatings(leagueId) {
  if (!ratingCache.has(leagueId)) {
    ratingCache.set(
      leagueId,
      api.leagueRatings(leagueId).then((rows) => Object.fromEntries(rows.map((row) => [row.club_id, row]))),
    )
  }
  return ratingCache.get(leagueId)
}

export function topLeague(leagues) {
  return leagues.find((league) => league.tier_rank === 1) ?? leagues[0] ?? null
}
