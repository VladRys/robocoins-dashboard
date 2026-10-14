import { Button as ButtonPrimitive } from '@base-ui/react'
import { cn } from 'cn'

import styles from './chip.module.css'

export interface ChipProps extends ButtonPrimitive.Props {
  selected?: boolean
  size?: 'md' | 'lg'
  tone?: 'brand' | 'error'
}

export function Chip({
  selected = false,
  size = 'md',
  tone = 'brand',
  className,
  children,
  ...props
}: ChipProps) {
  return (
    <ButtonPrimitive
      {...props}
      aria-pressed={selected}
      className={cn(styles.chip, styles[size], styles[tone], className)}
    >
      {children}
    </ButtonPrimitive>
  )
}
