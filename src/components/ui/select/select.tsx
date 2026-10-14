import { Select as SelectPrimitive } from '@base-ui/react/select'
import { cn } from 'cn'

import styles from './select.module.css'

export const Select = SelectPrimitive.Root

export interface SelectGroupProps extends SelectPrimitive.Group.Props {}

export function SelectGroup({ className, ...props }: SelectGroupProps) {
  return <SelectPrimitive.Group {...props} className={cn(styles.group, className)} />
}

export interface SelectValueProps extends SelectPrimitive.Value.Props {}

export function SelectValue({ className, ...props }: SelectValueProps) {
  return <SelectPrimitive.Value {...props} className={cn(styles.value, className)} />
}

export interface SelectTriggerProps extends SelectPrimitive.Trigger.Props {}

export function SelectTrigger({ className, children, ...props }: SelectTriggerProps) {
  return (
    <SelectPrimitive.Trigger {...props} className={cn(styles.trigger, className)}>
      {children}
      <SelectPrimitive.Icon
        className={styles.icon}
        render={<span className="i-ph:caret-down-bold" />}
      />
    </SelectPrimitive.Trigger>
  )
}

export interface SelectContentProps
  extends
    SelectPrimitive.Popup.Props,
    Pick<SelectPrimitive.Positioner.Props, 'side' | 'sideOffset' | 'align' | 'alignOffset'> {}

export function SelectContent({
  className,
  children,
  side = 'bottom',
  sideOffset = 6,
  align = 'center',
  alignOffset = 0,
  ...props
}: SelectContentProps) {
  return (
    <SelectPrimitive.Portal>
      <SelectPrimitive.Positioner
        side={side}
        sideOffset={sideOffset}
        align={align}
        alignOffset={alignOffset}
        alignItemWithTrigger={false}
        className={styles.positioner}
      >
        <SelectPrimitive.Popup {...props} className={cn(styles.content, className)}>
          <SelectPrimitive.List>{children}</SelectPrimitive.List>
        </SelectPrimitive.Popup>
      </SelectPrimitive.Positioner>
    </SelectPrimitive.Portal>
  )
}

export interface SelectLabelProps extends SelectPrimitive.GroupLabel.Props {}

export function SelectLabel({ className, ...props }: SelectLabelProps) {
  return <SelectPrimitive.GroupLabel {...props} className={cn(styles.label, className)} />
}

export interface SelectItemProps extends SelectPrimitive.Item.Props {}

export function SelectItem({ className, children, ...props }: SelectItemProps) {
  return (
    <SelectPrimitive.Item {...props} className={cn(styles.item, className)}>
      <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
      <SelectPrimitive.ItemIndicator
        className={styles.indicator}
        render={({ children: _children, ...indicatorProps }) => (
          <span {...indicatorProps} className="i-ph:check-bold" />
        )}
      />
    </SelectPrimitive.Item>
  )
}

export interface SelectSeparatorProps extends SelectPrimitive.Separator.Props {}

export function SelectSeparator({ className, ...props }: SelectSeparatorProps) {
  return <SelectPrimitive.Separator {...props} className={cn(styles.separator, className)} />
}
