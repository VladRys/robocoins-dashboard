import { createFileRoute, Outlet } from '@tanstack/react-router'
import { cn } from 'cn'

import { RegisterProvider } from './-components/register-provider/register-provider'
import { registerState } from './-lib'

import styles from './route.module.css'

export const Route = createFileRoute('/(auth)/register')({
  component: RouteComponent,
  loader: () => registerState.load(),
})

function RouteComponent() {
  const initialState = Route.useLoaderData()

  return (
    <div className={styles.wrapper}>
      <div className={cn('i-ph:coins', styles.coins)} />
      <RegisterProvider initialState={initialState}>
        <Outlet />
      </RegisterProvider>
    </div>
  )
}
