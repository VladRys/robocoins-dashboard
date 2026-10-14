import { createFileRoute, redirect } from '@tanstack/react-router'

import { LOCALSTORAGE_DID_REGISTER } from './-constants'

export const Route = createFileRoute('/_teacher')({
  beforeLoad: ({ context }) => {
    if (context.user?.role === 'student') throw redirect({ to: '/' })
    if (context.user?.role === 'teacher') return

    const to = localStorage.getItem(LOCALSTORAGE_DID_REGISTER) ? '/login' : '/register'
    throw redirect({ to })
  },
})
