import { Button as ButtonPrimitive } from "@base-ui/react";
import { cn } from "cn";

import styles from "./hero-button.module.css";

export interface HeroButtonProps extends ButtonPrimitive.Props {}

export function HeroButton({ className, children, ...props }: HeroButtonProps) {
  return (
    <ButtonPrimitive {...props} className={cn(styles.hero, className)}>
      {children}
    </ButtonPrimitive>
  );
}
