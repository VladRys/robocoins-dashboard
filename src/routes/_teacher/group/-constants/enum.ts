import { GroupTheme } from '../-mock'

export const StudentSortOrder = {
  NameAsc: 'name-asc',
  NameDesc: 'name-desc',
  BalanceDesc: 'balance-desc',
  BalanceAsc: 'balance-asc',
} as const

export type StudentSortOrder = (typeof StudentSortOrder)[keyof typeof StudentSortOrder]

export const GroupFilter = {
  All: 'all',
  ...GroupTheme,
} as const

export type GroupFilter = (typeof GroupFilter)[keyof typeof GroupFilter]
