import { useTranslate } from '@kanjou/react'
import { createFileRoute } from '@tanstack/react-router'
import { cn } from 'cn'

import { IconButton } from '#/components/ui'
import { getAvatarUrl } from '#/routes/-utils/get-avatar-url'

import { StudentDrawer, StudentSearchBar } from './-components'
import { useGroupStudentsPage } from './-hooks'

import styles from './$groupId.module.css'

export const Route = createFileRoute('/_teacher/group/$groupId')({
  component: RouteComponent,
})

function RouteComponent() {
  const { state, functions } = useGroupStudentsPage()

  const t = useTranslate()

  const hasStudents = !!state.students.length

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>{state.group?.title}</h1>
        <span className={styles.schedule}>{state.group?.schedule}</span>

        <IconButton
          className={styles['back-btn']}
          onClick={functions.handleBackToGroups}
          title={t('group.back')}
        >
          <span className="i-ph:arrow-left" />
        </IconButton>
      </header>

      <StudentSearchBar
        searchQuery={state.searchQuery}
        onSearchChange={functions.handleSearchChange}
        sortOrder={state.sortOrder}
        onSortChange={functions.handleSortChange}
      />

      {!hasStudents && <div className={styles.empty}>{t('student.empty')}</div>}

      {hasStudents && (
        <div className={styles['student-list']}>
          {state.students.map((student) => {
            return (
              <article
                key={student.id}
                className={styles['student-card']}
                onClick={() => functions.handleSelectStudent(student.id)}
              >
                <div className={styles['card-left']}>
                  <img
                    src={getAvatarUrl(student.avatar)}
                    alt={student.name}
                    className={styles.avatar}
                    draggable={false}
                  />
                  <span className={styles['student-name']}>{student.name}</span>
                </div>

                <div className={styles['card-right']}>
                  <div className={styles['balance-badge']}>
                    <span className={cn('i-ph:coins-bold', styles['coin-icon'])} />
                    <span>{student.balance}</span>
                  </div>
                  <span className={cn('i-ph:caret-right-bold', styles['caret-icon'])} />
                </div>
              </article>
            )
          })}
        </div>
      )}

      <StudentDrawer
        open={state.isDrawerOpen}
        student={state.selectedStudent}
        awards={state.studentAwards}
        onOpenChange={functions.handleDrawerOpenChange}
        onAward={functions.handleAward}
        onRevertAward={functions.handleRevertAward}
      />
    </div>
  )
}
