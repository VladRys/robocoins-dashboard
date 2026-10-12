import { createFileRoute, Outlet } from '@tanstack/react-router'
import { cn } from 'cn'

import styles from './route.module.css'

export const Route = createFileRoute('/(auth)')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className={styles.wrapper}>
      <div className={cn('i-ph:coins', styles.coins)} />
      <Outlet />
    </div>
  )
}
