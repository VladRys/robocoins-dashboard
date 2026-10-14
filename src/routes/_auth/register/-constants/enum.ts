export const AVATARS = ['skull', 'devil', 'dreamy', 'star-struck', 'cold'] as const
export type Avatar = (typeof AVATARS)[number]
