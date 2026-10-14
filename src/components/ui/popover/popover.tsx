import { Popover as PopoverPrimitive } from '@base-ui/react/popover'
import { cn } from 'cn'
import { ComponentProps } from 'react'

import styles from './popover.module.css'

export interface PopoverProps extends PopoverPrimitive.Root.Props {}

export function Popover(props: PopoverProps) {
  return <PopoverPrimitive.Root {...props} />
}

export interface PopoverTriggerProps extends PopoverPrimitive.Trigger.Props {}

export function PopoverTrigger(props: PopoverTriggerProps) {
  return <PopoverPrimitive.Trigger {...props} />
}

export interface PopoverCloseProps extends PopoverPrimitive.Close.Props {}

export function PopoverClose(props: PopoverCloseProps) {
  return <PopoverPrimitive.Close {...props} />
}

export interface PopoverContentProps
  extends
    PopoverPrimitive.Popup.Props,
    Pick<PopoverPrimitive.Positioner.Props, 'side' | 'sideOffset' | 'align' | 'alignOffset'> {}

export function PopoverContent({
  className,
  side = 'bottom',
  sideOffset = 6,
  align = 'center',
  alignOffset = 0,
  ...props
}: PopoverContentProps) {
  return (
    <PopoverPrimitive.Portal>
      <PopoverPrimitive.Positioner
        side={side}
        sideOffset={sideOffset}
        align={align}
        alignOffset={alignOffset}
        className={styles.positioner}
      >
        <PopoverPrimitive.Popup {...props} className={cn(styles.content, className)} />
      </PopoverPrimitive.Positioner>
    </PopoverPrimitive.Portal>
  )
}

export interface PopoverHeaderProps extends ComponentProps<'div'> {}

export function PopoverHeader({ className, ...props }: PopoverHeaderProps) {
  return <div {...props} className={cn(styles.header, className)} />
}

export interface PopoverTitleProps extends PopoverPrimitive.Title.Props {}

export function PopoverTitle({ className, ...props }: PopoverTitleProps) {
  return <PopoverPrimitive.Title {...props} className={cn(styles.title, className)} />
}

export interface PopoverDescriptionProps extends PopoverPrimitive.Description.Props {}

export function PopoverDescription({ className, ...props }: PopoverDescriptionProps) {
  return <PopoverPrimitive.Description {...props} className={cn(styles.description, className)} />
}
