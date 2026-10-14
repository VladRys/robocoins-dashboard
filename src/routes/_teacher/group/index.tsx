import { useTranslate } from '@kanjou/react'
import { createFileRoute } from '@tanstack/react-router'
import { cn } from 'cn'

import { Chip } from '#/components/ui'

import { GroupFilter } from './-constants'
import { useGroupPage } from './-hooks'

import styles from './index.module.css'

export const Route = createFileRoute('/_teacher/group/')({
  component: RouteComponent,
})

const GROUP_FILTERS = [
  { filter: GroupFilter.All, icon: null },
  { filter: GroupFilter.GameDev, icon: 'i-ph:game-controller' },
  { filter: GroupFilter.Web, icon: 'i-ph:code' },
  { filter: GroupFilter.Embedded, icon: 'i-ph:cpu' },
] as const

function RouteComponent() {
  const { state, functions } = useGroupPage()

  const t = useTranslate()

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>{t('group.select.title')}</h1>
      </header>

      <div className={styles['themes-bar']}>
        {GROUP_FILTERS.map((item) => {
          const isSelected = state.selectedTheme === item.filter
          const isAll = item.filter === GroupFilter.All

          return (
            <Chip
              key={item.filter}
              selected={isSelected}
              onClick={() => functions.handleThemeSelect(item.filter)}
            >
              {item.icon && <span className={item.icon} />}
              {isAll && <span>{t('group.filter.all', { count: state.allGroupsCount })}</span>}
              {!isAll && <span>{t(`group.theme.${item.filter}`)}</span>}
            </Chip>
          )
        })}
      </div>

      <div className={styles.grid}>
        {state.groups.map((group) => {
          return (
            <article
              key={group.id}
              className={cn(styles.card, styles[group.theme])}
              onClick={() => functions.handleGroupClick(group.id)}
            >
              <div className={styles['card-top']}>
                <div className={styles['card-title-group']}>
                  <div className={styles['card-icon']}>
                    <span className={group.icon} />
                  </div>
                  <div>
                    <h2 className={styles['card-title']}>{group.title}</h2>
                    <span className={styles['card-theme-tag']}>
                      {t(`group.theme.${group.theme}`)}
                    </span>
                  </div>
                </div>

                <div className={styles['card-meta']}>
                  <span className={styles['students-count']}>
                    {t('group.students-count', { count: group.studentCount })}
                  </span>
                  <span className={cn('i-ph:caret-right-bold', styles['arrow-icon'])} />
                </div>
              </div>

              <div className={styles['card-footer']}>
                <div className={styles['schedule-block']}>
                  <span className={cn('i-ph:clock-bold', styles['schedule-icon'])} />
                  <span>{group.schedule}</span>
                </div>
              </div>
            </article>
          )
        })}
      </div>
    </div>
  )
}
