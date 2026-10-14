import { useTranslate } from '@kanjou/react'
import { cn } from 'cn'
import { useEffect, useRef, useState } from 'react'

import { Chip, Drawer, DrawerContent, DrawerHeader, DrawerTitle } from '#/components/ui'
import { getAvatarUrl } from '#/routes/-utils/get-avatar-url'

import { AwardReason, Student, StudentAward } from '../../-mock'
import { AwardDirection } from '../../-types'

import styles from './student-drawer.module.css'

const REASON_DEBOUNCE_IN_MILLISECONDS = 800

const POSITIVE_REASONS: AwardReason[] = [
  'activity',
  'homework',
  'teamwork',
  'answer',
  'initiative',
  'other',
]

const NEGATIVE_REASONS: AwardReason[] = ['discipline', 'mistake', 'late', 'incomplete', 'other']

export interface StudentDrawerProps {
  open: boolean
  student: Student | null
  awards: StudentAward[]
  onOpenChange: (open: boolean) => void
  onAward: (studentId: string, amount: number, reason: AwardReason) => void
  onRevertAward: (awardId: string) => void
}

export function StudentDrawer({
  open,
  student,
  awards,
  onOpenChange,
  onAward,
  onRevertAward,
}: StudentDrawerProps) {
  const t = useTranslate()
  const [direction, setDirection] = useState<AwardDirection>(1)
  const [selectedAwardId, setSelectedAwardId] = useState<string | null>(null)
  const [pendingReason, setPendingReason] = useState<AwardReason | null>(null)
  const timeoutReference = useRef<ReturnType<typeof setTimeout>>(undefined)

  function cancelPendingReason() {
    clearTimeout(timeoutReference.current)
    setPendingReason(null)
  }

  function resetState() {
    cancelPendingReason()
    setDirection(1)
    setSelectedAwardId(null)
  }

  useEffect(() => {
    if (!open) resetState()
  }, [open])

  useEffect(() => {
    return () => {
      clearTimeout(timeoutReference.current)
    }
  }, [])

  function handleOpenChange(isOpen: boolean) {
    if (!isOpen) resetState()
    onOpenChange(isOpen)
  }

  function handleDirectionSelect(selectedDirection: AwardDirection) {
    cancelPendingReason()
    setDirection(selectedDirection)
  }

  function handleReasonClick(reason: AwardReason) {
    if (!student) return

    if (pendingReason === reason) {
      cancelPendingReason()
      return
    }

    clearTimeout(timeoutReference.current)
    setPendingReason(reason)
    timeoutReference.current = setTimeout(() => {
      onAward(student.id, direction, reason)
    }, REASON_DEBOUNCE_IN_MILLISECONDS)
  }

  function handleAwardSelect(awardId: string) {
    if (selectedAwardId === awardId) {
      setSelectedAwardId(null)
      return
    }
    setSelectedAwardId(awardId)
  }

  function handleRevertSelectedAward() {
    if (!selectedAwardId) return

    onRevertAward(selectedAwardId)
    setSelectedAwardId(null)
  }

  const isPlus = direction === 1
  const isMinus = direction === -1
  const hasSelectedAward = Boolean(selectedAwardId)
  const hasAwards = !!awards.length

  return (
    <Drawer open={open} onOpenChange={handleOpenChange} showSwipeHandle>
      <DrawerContent>
        {student && (
          <>
            <DrawerHeader>
              <div className={cn(styles['student-wrap'])}>
                <img
                  src={getAvatarUrl(student.avatar)}
                  alt={student.name}
                  className={cn(styles.avatar)}
                  draggable={false}
                />
                <DrawerTitle>{student.name}</DrawerTitle>
              </div>
            </DrawerHeader>

            <div className={cn(styles['direction-toggle'])}>
              <button
                type="button"
                className={cn(
                  styles['direction-btn'],
                  isPlus && styles['direction-btn-plus-active'],
                )}
                onClick={() => handleDirectionSelect(1)}
              >
                <span className={cn('i-ph:coins-bold', styles['coin-icon'])} />
                <span>+1</span>
              </button>
              <button
                type="button"
                className={cn(
                  styles['direction-btn'],
                  isMinus && styles['direction-btn-minus-active'],
                )}
                onClick={() => handleDirectionSelect(-1)}
              >
                <span className={cn('i-ph:coins-bold', styles['coin-icon'])} />
                <span>-1</span>
              </button>
            </div>

            <div>
              <span className={cn(styles['section-label'])}>{t('award.reason.label')}</span>
              <div className={cn(styles['reasons-list'])}>
                {isPlus &&
                  POSITIVE_REASONS.map((reason) => {
                    return (
                      <Chip
                        key={reason}
                        size="lg"
                        selected={pendingReason === reason}
                        onClick={() => handleReasonClick(reason)}
                      >
                        {t(`reason.${reason}`)}
                      </Chip>
                    )
                  })}

                {isMinus &&
                  NEGATIVE_REASONS.map((reason) => {
                    return (
                      <Chip
                        key={reason}
                        size="lg"
                        tone="error"
                        selected={pendingReason === reason}
                        onClick={() => handleReasonClick(reason)}
                      >
                        {t(`reason.${reason}`)}
                      </Chip>
                    )
                  })}
              </div>
            </div>

            <div className={cn(styles['history-section'])}>
              <div className={cn(styles['history-header'])}>
                <span className={cn(styles['section-label'])}>{t('award.history.title')}</span>
                {hasSelectedAward && (
                  <button
                    type="button"
                    className={cn(styles['revert-btn'])}
                    onClick={handleRevertSelectedAward}
                  >
                    <span className={cn('i-ph:arrow-u-up-left')} />
                    <span>{t('action.revert.title')}</span>
                  </button>
                )}
              </div>

              {!hasAwards && (
                <div className={cn(styles['history-empty'])}>{t('award.history.empty')}</div>
              )}

              {hasAwards && (
                <div className={cn(styles['history-list'])}>
                  {awards.map((award) => {
                    const isSelected = award.id === selectedAwardId
                    const isAwardPlus = award.amount > 0

                    return (
                      <button
                        key={award.id}
                        type="button"
                        className={cn(
                          styles['history-item'],
                          isSelected && styles['history-item-selected'],
                        )}
                        onClick={() => handleAwardSelect(award.id)}
                      >
                        <div className={cn(styles['history-left'])}>
                          <span
                            className={cn(
                              styles['history-amount'],
                              isAwardPlus && styles['history-amount-plus'],
                              !isAwardPlus && styles['history-amount-minus'],
                            )}
                          >
                            {isAwardPlus && `+${award.amount}`}
                            {!isAwardPlus && `${award.amount}`}
                          </span>
                          <div className={cn(styles['history-details'])}>
                            <span className={cn(styles['history-reason'])}>
                              {t(`reason.${award.reason}`)}
                            </span>
                            <span className={cn(styles['history-time'])}>{award.timestamp}</span>
                          </div>
                        </div>

                        {isSelected && (
                          <span className={cn('i-ph:check-circle-fill', styles['check-icon'])} />
                        )}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </DrawerContent>
    </Drawer>
  )
}
