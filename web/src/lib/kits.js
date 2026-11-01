import { api } from './api.js'

export const KIT_LABELS = {
  main: 'Домашняя',
  white: 'Гостевая',
  black: 'Дополнительная 1',
  reserve: 'Дополнительная 2',
}

const cache = new Map()

export function loadKitSpecs(teamId) {
  if (!cache.has(teamId)) cache.set(teamId, api.kitSpecs(teamId))
  return cache.get(teamId)
}

export function kitLabel(kit) {
  return KIT_LABELS[kit?.id] ?? 'Комплект'
}
