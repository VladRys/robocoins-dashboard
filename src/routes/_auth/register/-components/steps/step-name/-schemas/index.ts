import { z } from 'zod'

export const StepNameSchema = z.object({
  name: z.string().trim().min(1),
})
