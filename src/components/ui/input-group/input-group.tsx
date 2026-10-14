import { Input as InputPrimitive } from '@base-ui/react'
import { cn } from 'cn'
import { ComponentProps, MouseEvent } from 'react'

import styles from './input-group.module.css'

export interface InputGroupProps extends ComponentProps<'div'> {
  size?: 'sm' | 'md' | 'lg'
}

export function InputGroup({
  size = 'md',
  className,
  children,
  onClick,
  ...props
}: InputGroupProps) {
  function handleClick(event: MouseEvent<HTMLDivElement>) {
    onClick?.(event)

    if ((event.target as HTMLElement).closest('button')) {
      return
    }

    event.currentTarget
      .querySelector<HTMLInputElement | HTMLTextAreaElement>('input, textarea')
      ?.focus()
  }

  return (
    <div
      {...props}
      role="group"
      data-slot="input-group"
      className={cn(styles.group, styles[size], className)}
      onClick={handleClick}
    >
      {children}
    </div>
  )
}

export interface InputGroupAddonProps extends ComponentProps<'div'> {
  align?: 'inline-start' | 'inline-end' | 'block-start' | 'block-end'
}

export function InputGroupAddon({
  align = 'inline-start',
  className,
  onClick,
  ...props
}: InputGroupAddonProps) {
  function handleClick(event: MouseEvent<HTMLDivElement>) {
    onClick?.(event)

    if ((event.target as HTMLElement).closest('button')) {
      return
    }

    event.currentTarget.parentElement
      ?.querySelector<HTMLInputElement | HTMLTextAreaElement>('input, textarea')
      ?.focus()
  }

  return (
    <div
      {...props}
      role="group"
      data-slot="input-group-addon"
      data-align={align}
      className={cn(styles.addon, styles[align], className)}
      onClick={handleClick}
    />
  )
}

export interface InputGroupButtonProps extends ComponentProps<'button'> {
  size?: 'xs' | 'sm' | 'md'
}

export function InputGroupButton({
  type = 'button',
  size = 'sm',
  className,
  ...props
}: InputGroupButtonProps) {
  return (
    <button
      {...props}
      type={type}
      data-slot="input-group-button"
      className={cn(styles.button, styles[`button-${size}`], className)}
    />
  )
}

export interface InputGroupTextProps extends ComponentProps<'span'> {}

export function InputGroupText({ className, ...props }: InputGroupTextProps) {
  return <span {...props} data-slot="input-group-text" className={cn(styles.text, className)} />
}

export interface InputGroupInputProps extends InputPrimitive.Props {}

export function InputGroupInput({ className, ...props }: InputGroupInputProps) {
  return (
    <InputPrimitive
      {...props}
      data-slot="input-group-control"
      className={cn(styles.input, className)}
    />
  )
}

export interface InputGroupTextareaProps extends ComponentProps<'textarea'> {}

export function InputGroupTextarea({ className, ...props }: InputGroupTextareaProps) {
  return (
    <textarea
      {...props}
      data-slot="input-group-control"
      className={cn(styles.textarea, className)}
    />
  )
}
