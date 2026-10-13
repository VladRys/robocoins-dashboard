import { createFileRoute, redirect } from '@tanstack/react-router'

import { LOCALSTORAGE_DID_REGISTER } from './-constants'

export const Route = createFileRoute('/')({
  component: RouteComponent,
  beforeLoad: ({ context }) => {
    if (context.user) throw redirect({ to: '/profile' })

    const to = localStorage.getItem(LOCALSTORAGE_DID_REGISTER) ? '/login' : '/register'

    throw redirect({ to })
  },
})

function RouteComponent() {
  return <div>Hello "/"!</div>
}
