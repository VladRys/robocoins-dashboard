import { z } from 'zod'

export const PasswordSchema = z.string()

export const LoginStateSchema = z.object({
  password: PasswordSchema,
})
