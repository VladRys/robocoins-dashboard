import { createFileRoute, redirect } from '@tanstack/react-router'

import { LOCALSTORAGE_DID_REGISTER } from './-constants'

export const Route = createFileRoute('/_student')({
  beforeLoad: ({ context }) => {
    if (context.user?.role === 'teacher') throw redirect({ to: '/group' })
    if (context.user?.role === 'student') return

    const to = localStorage.getItem(LOCALSTORAGE_DID_REGISTER) ? '/login' : '/register'
    throw redirect({ to })
  },
})
