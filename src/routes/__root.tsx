import { Outlet, createRootRouteWithContext } from '@tanstack/react-router'

import { NotFound } from './-components/not-found'
import { Avatar } from './_auth/register/-constants'

interface User {
  name: string
  avatar: Avatar
  balance: number
  role: 'admin' | 'teacher' | 'student'
}

export interface RootContext {
  user: User | null
}

export const Route = createRootRouteWithContext<RootContext>()({
  component: RootComponent,
  notFoundComponent: NotFound,
  loader: () => {},
})

function RootComponent() {
  return (
    <div className="h-screen">
      <Outlet />
    </div>
  )
}
