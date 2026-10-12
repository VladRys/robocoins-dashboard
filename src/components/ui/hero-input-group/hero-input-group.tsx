import { cn } from 'cn'
import type { ComponentProps, MouseEvent, ReactNode } from 'react'

import { HeroInput, type HeroInputProps } from '../hero-input'

import styles from './hero-input-group.module.css'

export interface HeroInputGroupProps extends ComponentProps<'div'> {
  children?: ReactNode
}

export function HeroInputGroup({ className, children, onClick, ...props }: HeroInputGroupProps) {
  const handleClick = (event: MouseEvent<HTMLDivElement>) => {
    onClick?.(event)

    if ((event.target as HTMLElement).closest('button')) return

    event.currentTarget.querySelector('input')?.focus()
  }

  return (
    <div
      {...props}
      role="group"
      data-slot="input-group"
      className={cn(styles.group, className)}
      onClick={handleClick}
    >
      {children}
    </div>
  )
}

export interface HeroInputGroupInputProps extends HeroInputProps {}

export function HeroInputGroupInput({ className, ...props }: HeroInputGroupInputProps) {
  return <HeroInput {...props} className={className} />
}

export interface HeroInputGroupButtonProps extends ComponentProps<'button'> {}

export function HeroInputGroupButton({
  className,
  type = 'button',
  ...props
}: HeroInputGroupButtonProps) {
  return (
    <button
      {...props}
      type={type}
      data-slot="input-group-button"
      className={cn(styles.button, className)}
    />
  )
}
