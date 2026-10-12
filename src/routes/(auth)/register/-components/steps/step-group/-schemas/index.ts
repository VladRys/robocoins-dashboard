import { z } from 'zod'

export const StepGroupSchema = z
  .object({
    courseName: z.string().trim().min(1),
    groupId: z.string().trim(),
  })
  .superRefine((value, context) => {
    if (value.courseName && !value.groupId) {
      context.addIssue({ code: 'custom', message: 'group required', path: ['groupId'] })
    }
  })
