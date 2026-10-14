export const LOCALSTORAGE_REGISTER_STATE = 'registerDraft'

export const AVATARS = ['skull', 'devil', 'dreamy', 'star-struck', 'cold'] as const
export type Avatar = (typeof AVATARS)[number]
