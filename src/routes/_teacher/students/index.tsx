import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/_teacher/students/')({
  beforeLoad: () => {
    throw redirect({ to: '/group' })
  },
  component: () => null,
})
