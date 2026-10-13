import { useTranslate } from '@kanjou/react'
import { createFileRoute } from '@tanstack/react-router'
import { cn } from 'cn'

import { Typography } from '#/components/ui'

import { useProfilePage } from './-hooks'

import styles from './index.module.css'

export const Route = createFileRoute('/profile/')({
  component: RouteComponent,
  beforeLoad: ({ context }) => {
    if (context.user) return

    //         const to = localStorage.getItem(LOCALSTORAGE_DID_REGISTER) ? '/login' : '/register'
    //         throw redirect({ to })
  },
})

function RouteComponent() {
  const { state } = useProfilePage()
  const t = useTranslate()

  return (
    <section className={styles.page}>
      <div className={cn('i-ph:coins-bold', styles.coins)} />

      <header className={styles.header}>
        <img src={state.avatar} draggable={false} className={styles.avatar} />
        <Typography variant="subtitle">{state.name}</Typography>
      </header>

      <div className={styles.balance}>
        <span className={styles.amount}>
          {t('profile.balance.amount', { count: state.balance })}
        </span>
        <Typography variant="caption">
          {t('profile.balance.caption', { count: state.balance })}
        </Typography>
      </div>
    </section>
  )
}
