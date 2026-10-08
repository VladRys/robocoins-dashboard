export const LOCALSTORAGE_REGISTER_STATE = 'registerDraft'

export const AVATARS = {
  skull: '/skull.png',
  devil: '/devil.png',
  dreamy: '/dreamy.png',
  'star-struck': '/star-struck.png',
  cold: '/cold.png',
} as const
export type AvatarKey = keyof typeof AVATARS

export const AVATAR_KEYS = Object.keys(AVATARS) as AvatarKey[]
