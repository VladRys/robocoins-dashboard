import { Button as ButtonPrimitive } from '@base-ui/react'
import { cn } from 'cn'

import styles from './icon-button.module.css'

export interface IconButtonProps extends ButtonPrimitive.Props {
  variant: 'contain'
  size: 'sm' | 'md' | 'lg'
}

export function IconButton({ variant, size, children, ...props }: IconButtonProps) {
  return (
    <ButtonPrimitive {...props} className={cn(styles.button, styles[variant], styles[size])}>
      {children}
    </ButtonPrimitive>
  )
}
