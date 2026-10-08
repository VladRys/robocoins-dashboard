import { Outlet, createRootRouteWithContext } from '@tanstack/react-router'

interface User {
  name: string
  role: 'admin' | 'user'
}

export interface RootContext {
  user: User | null
}

export const Route = createRootRouteWithContext<RootContext>()({
  component: RootComponent,
})

function RootComponent() {
  return (
    <div className="h-screen">
      <Outlet />
    </div>
  )
}
