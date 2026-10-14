import { createFileRoute } from '@tanstack/react-router'
import { ComponentType } from 'react'

import { useRegisterContext } from './-components/register-provider'
import { StepAvatar, StepGroup, StepName, StepView } from './-components/steps'
import { RegisterStep } from './-schemas'

export const Route = createFileRoute('/_auth/register/')({
  component: RouteComponent,
})

const STEPS: Record<RegisterStep, ComponentType> = {
  name: StepName,
  group: StepGroup,
  avatar: StepAvatar,
  view: StepView,
}

function RouteComponent() {
  const { state } = useRegisterContext()

  const Step = STEPS[state.step]

  return <Step />
}
