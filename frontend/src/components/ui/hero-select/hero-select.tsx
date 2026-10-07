import { Select as SelectPrimitive } from "@base-ui/react/select";
import { cn } from "cn";

import styles from "./hero-select.module.css";

export const HeroSelect = SelectPrimitive.Root;

export interface HeroSelectValueProps extends SelectPrimitive.Value.Props {}

export function HeroSelectValue({ className, ...props }: HeroSelectValueProps) {
  return <SelectPrimitive.Value {...props} className={cn(styles.value, className)} />;
}

export interface HeroSelectTriggerProps extends SelectPrimitive.Trigger.Props {}

export function HeroSelectTrigger({ className, children, ...props }: HeroSelectTriggerProps) {
  return (
    <div className={cn(styles.hero, className)}>
      <SelectPrimitive.Trigger {...props} className={styles.trigger}>
        {children}
        <SelectPrimitive.Icon
          className={styles.icon}
          render={<div className="i-ph:caret-down-bold" />}
        />
      </SelectPrimitive.Trigger>
      <div />
    </div>
  );
}

export interface HeroSelectContentProps
  extends
    SelectPrimitive.Popup.Props,
    Pick<SelectPrimitive.Positioner.Props, "side" | "sideOffset" | "align" | "alignOffset"> {}

export function HeroSelectContent({
  className,
  children,
  side = "bottom",
  sideOffset = 8,
  align = "center",
  alignOffset = 0,
  ...props
}: HeroSelectContentProps) {
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
  );
}

export interface HeroSelectItemProps extends SelectPrimitive.Item.Props {}

export function HeroSelectItem({ className, children, ...props }: HeroSelectItemProps) {
  return (
    <SelectPrimitive.Item {...props} className={cn(styles.item, className)}>
      <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
      <SelectPrimitive.ItemIndicator
        className={styles.indicator}
        render={({ children: _children, ...props }) => (
          <div {...props} className="i-ph:check-bold" />
        )}
      />
    </SelectPrimitive.Item>
  );
}
