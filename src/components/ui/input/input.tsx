import { Input as InputPrimitive } from '@base-ui/react'
import { cn } from 'cn'

import styles from './input.module.css'

export interface InputProps extends Omit<InputPrimitive.Props, 'size'> {
  variant?: 'contain'
  size?: 'sm' | 'md' | 'lg'
}

export function Input({ variant = 'contain', size = 'md', ...props }: InputProps) {
  return <InputPrimitive {...props} className={cn(styles.input, styles[variant], styles[size])} />
}
