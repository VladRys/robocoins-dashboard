import { createFileRoute, redirect } from '@tanstack/react-router'
import { ComponentType } from 'react'

import { RegisterStep, useRegisterContext } from './-components/register-provider/register-provider'
import { StepAvatar, StepGroup, StepName, StepView } from './-components/steps'

export const Route = createFileRoute('/(auth)/register/')({
  component: RouteComponent,
  beforeLoad: ({ context }) => {
    if (context.user) throw redirect({ to: '/' })
  },
})

const STEPS: Record<RegisterStep, ComponentType> = {
  name: StepName,
  group: StepGroup,
  avatar: StepAvatar,
  view: StepView,
}

function RouteComponent() {
  const register = useRegisterContext()

  const Step = STEPS[register.state.step]

  return <Step />
}
