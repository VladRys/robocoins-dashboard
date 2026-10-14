import { Avatar } from '#/routes/_auth/register/-constants'

export const GroupTheme = {
  GameDev: 'game-dev',
  Web: 'web',
  Embedded: 'embedded',
} as const

export type GroupTheme = (typeof GroupTheme)[keyof typeof GroupTheme]

export interface Group {
  id: string
  title: string
  theme: GroupTheme
  studentCount: number
  schedule: string
  icon: string
}

export type StudentStatus = 'active' | 'away' | 'offline'

export interface Student {
  id: string
  groupId: string
  name: string
  avatar: Avatar
  balance: number
  status: StudentStatus
  lastActive: string
  attendanceRate: number
  completedTasks: number
}

export type AwardReason =
  | 'activity'
  | 'homework'
  | 'teamwork'
  | 'answer'
  | 'initiative'
  | 'discipline'
  | 'mistake'
  | 'late'
  | 'incomplete'
  | 'other'

export interface StudentAward {
  id: string
  studentId: string
  amount: number
  reason: AwardReason
  timestamp: string
}

export interface CreateAwardPayload {
  studentId: string
  amount: number
  reason: AwardReason
}
