import { z } from 'zod'

import { AVATAR_KEYS } from '../-constants'

export const RegisterStep = {
  Name: 'name',
  Group: 'group',
  Avatar: 'avatar',
  View: 'view',
} as const

export const RegisterStateSchema = z.object({
  step: z.enum(RegisterStep),
  name: z.string().trim().min(1).optional(),
  avatar: z.enum(AVATAR_KEYS).optional(),
  courseName: z.string().min(1).optional(),
  groupId: z.number().int().positive().optional(),
})

export type RegisterState = z.infer<typeof RegisterStateSchema>
export type RegisterStep = RegisterState['step']

export const CompleteRegisterStateSchema = RegisterStateSchema.required({
  name: true,
  avatar: true,
  courseName: true,
  groupId: true,
})

export const DEFAULT_REGISTER_STATE: RegisterState = { step: RegisterStep.Name }

export const JsonSchema = z.string().transform((value, context) => {
  try {
    return JSON.parse(value)
  } catch {
    context.addIssue({ code: 'custom', message: 'validation.invalid-json' })
    return z.NEVER
  }
})
