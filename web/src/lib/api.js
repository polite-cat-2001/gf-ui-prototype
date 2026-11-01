async function request(path, options = {}) {
  const response = await fetch(path, options)
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const payload = await response.json()
      if (typeof payload.detail === 'string') detail = payload.detail
      else if (payload.detail) detail = JSON.stringify(payload.detail)
    } catch {
      // Keep the HTTP status when the error body is not JSON.
    }
    throw new Error(detail)
  }
  return response.json()
}

function get(path) {
  return request(path)
}

export const api = {
  meta: () => get('/api/meta'),
  countries: () => get('/api/countries'),
  leagues: (countryId) => get(`/api/leagues?country_id=${encodeURIComponent(countryId)}`),
  clubs: (leagueId) => get(`/api/clubs?league_id=${encodeURIComponent(leagueId)}`),
  club: (clubId) => get(`/api/clubs/${encodeURIComponent(clubId)}`),
  squad: (clubId) => get(`/api/clubs/${encodeURIComponent(clubId)}/players`),
  clubRatings: (clubId) => get(`/api/clubs/${encodeURIComponent(clubId)}/ratings`),
  leagueRatings: (leagueId) => get(`/api/leagues/${encodeURIComponent(leagueId)}/ratings`),
  nationalTeams: () => get('/api/national-teams'),
  nationalSquad: (teamId) => get(`/api/national-teams/${encodeURIComponent(teamId)}/players`),
  kits: (clubId) => get(`/api/clubs/${encodeURIComponent(clubId)}/kits`),
  kitSpecs: (teamId) => get(`/api/teams/${encodeURIComponent(teamId)}/kit-specs`),
}
