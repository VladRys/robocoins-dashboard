import { createFileRoute, Outlet } from "@tanstack/react-router";
import { RegisterProvider } from "./-components/register-provider/register-provider";

import styles from "./route.module.css";
import { cn } from "cn";

export const Route = createFileRoute("/(auth)/register")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className={styles.wrapper}>
      <div className={cn("i-ph:coins", styles.coins)} />
      <RegisterProvider>
        <Outlet />
      </RegisterProvider>
    </div>
  );
}
