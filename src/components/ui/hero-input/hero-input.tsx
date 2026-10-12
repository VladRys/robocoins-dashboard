import { Input as InputPrimitive } from '@base-ui/react'
import { cn } from 'cn'

import styles from './hero-input.module.css'

export interface HeroInputProps extends Omit<InputPrimitive.Props, 'size'> {
  className?: string
}

export function HeroInput({ className, ...props }: HeroInputProps) {
  return (
    <div className={cn(styles.hero, className)}>
      <InputPrimitive {...props} className={styles.input} />
    </div>
  )
}
