import { cn } from "cn";

import styles from "./loader.module.css";

export function Loader() {
  return (
    <div className={styles.loader}>
      <div className={cn("i-ph:circle-notch", styles.icon)} />
    </div>
  );
}
