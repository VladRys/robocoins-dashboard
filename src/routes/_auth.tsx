import { createFileRoute, Outlet, redirect } from '@tanstack/react-router'
import { cn } from 'cn'

import styles from './_auth.module.css'

export const Route = createFileRoute('/_auth')({
  component: RouteComponent,
  beforeLoad: ({ context }) => {
    if (context.user?.role === 'student') throw redirect({ to: '/' })
    if (context.user?.role === 'teacher') throw redirect({ to: '/students' })
  },
})

function RouteComponent() {
  return (
    <div className={styles.wrapper}>
      <div className={cn('i-ph:coins', styles.coins)} />
      <Outlet />
    </div>
  )
}
