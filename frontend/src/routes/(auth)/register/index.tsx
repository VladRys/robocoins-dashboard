import { ComponentType } from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";

import { RegisterStep, useRegisterContext } from "./-components/register-provider/register-provider";
import { StepName } from "./-components/steps";

export const Route = createFileRoute("/(auth)/register/")({
  component: RouteComponent,
  beforeLoad: ({ context }) => {
    if (context.user) throw redirect({ to: "/" });
  },
});

const STEPS: Record<RegisterStep, ComponentType> = {
  name: StepName,
};

function RouteComponent() {
  const { step } = useRegisterContext();

  const Step = STEPS[step];

  return <Step />;
}
