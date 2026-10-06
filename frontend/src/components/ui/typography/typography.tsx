import { cn } from "cn";
import { ComponentProps } from "react";

import styles from "./typography.module.css";

export interface TypographyProps extends ComponentProps<"div"> {
  variant: "title" | "caption";
}

export function Typography({
  variant,
  children,
  className,
  ...props
}: TypographyProps) {
  return (
    <div
      {...props}
      className={cn(styles.typography, styles[variant], className)}
    >
      {children}
    </div>
  );
}
