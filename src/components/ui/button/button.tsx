import { Button as ButtonPrimitive } from '@base-ui/react'
import { cn } from 'cn'

import styles from './button.module.css'

export interface ButtonProps extends ButtonPrimitive.Props {
  variant?: 'contain' | 'ghost' | 'link'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  variant = 'contain',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <ButtonPrimitive
      {...props}
      className={cn(styles.button, styles[variant], styles[size], className)}
    >
      {children}
    </ButtonPrimitive>
  )
}
