import { useTranslate } from '@kanjou/react'
import { cn } from 'cn'
import { ChangeEvent } from 'react'

import {
  IconButton,
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
  Popover,
  PopoverClose,
  PopoverContent,
  PopoverTitle,
  PopoverTrigger,
} from '#/components/ui'

import { StudentSortOrder } from '../../-constants'

import styles from './student-search-bar.module.css'

export interface StudentSearchBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  sortOrder: StudentSortOrder
  onSortChange: (sortOrder: StudentSortOrder) => void
}

const SORT_ORDERS = Object.values(StudentSortOrder)

export function StudentSearchBar({
  searchQuery,
  onSearchChange,
  sortOrder,
  onSortChange,
}: StudentSearchBarProps) {
  const t = useTranslate()

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    onSearchChange(event.target.value)
  }

  function handleClearSearch() {
    onSearchChange('')
  }

  const hasSearchValue = !!searchQuery

  return (
    <div className={styles.row}>
      <InputGroup className={styles['search-wrapper']}>
        <InputGroupAddon align="inline-start">
          <span className="i-ph:magnifying-glass" />
        </InputGroupAddon>
        <InputGroupInput
          type="text"
          placeholder={t('field.student-search.placeholder')}
          value={searchQuery}
          onChange={handleInputChange}
        />
        {hasSearchValue && (
          <InputGroupAddon align="inline-end">
            <InputGroupButton onClick={handleClearSearch} title={t('action.clear-search.title')}>
              <span className="i-ph:x" />
            </InputGroupButton>
          </InputGroupAddon>
        )}
      </InputGroup>

      <Popover>
        <PopoverTrigger render={<IconButton title={t('sort.students')} />}>
          <span className="i-ph:arrows-down-up" />
        </PopoverTrigger>

        <PopoverContent align="end">
          <PopoverTitle className={styles['popover-title']}>{t('sort.title')}</PopoverTitle>
          {SORT_ORDERS.map((order) => {
            const isActive = sortOrder === order

            return (
              <PopoverClose
                key={order}
                className={styles['popover-option']}
                data-active={isActive || undefined}
                onClick={() => onSortChange(order)}
              >
                <span>{t(`sort.${order}`)}</span>
                {isActive && <span className={cn('i-ph:check-bold', styles['check-icon'])} />}
              </PopoverClose>
            )
          })}
        </PopoverContent>
      </Popover>
    </div>
  )
}
