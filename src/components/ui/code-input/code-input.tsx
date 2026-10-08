import { cn } from 'cn'
import { Fragment } from 'react'

import styles from './code-input.module.css'

export interface CodeInputProps {
  value?: string
}

const ITERATED = Array.from({ length: 4 }).map((_, i) => i)

export function CodeInput({ value = '' }: CodeInputProps) {
  const asteriskAt = value.padEnd(4, ' ').indexOf(' ')

  return (
    <div className={styles['code-input']}>
      {ITERATED.map((i) => {
        return (
          <Fragment key={i}>
            {i !== asteriskAt && <span>{value[i]}</span>}
            {i === asteriskAt && <div className={cn(styles.hint, 'i-custom:asterisk')} />}
            {i !== 3 && <div className={styles.divider} />}
          </Fragment>
        )
      })}
    </div>
  )
}
