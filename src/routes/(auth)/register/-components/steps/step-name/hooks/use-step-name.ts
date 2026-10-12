import { useForm } from '@tanstack/react-form'
import type { SyntheticEvent } from 'react'

import { StepNameSchema } from '../-schemas'
import { RegisterStep } from '../../../../-schemas'
import { useRegisterContext } from '../../../register-provider'

export function useStepName() {
  const register = useRegisterContext()

  const form = useForm({
    defaultValues: { name: register.state.name ?? '' },
    validators: { onChange: StepNameSchema },
    onSubmit: ({ value }) => {
      register.setState({ step: RegisterStep.Group, name: value.name.trim() })
    },
  })

  const handleSubmit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault()
    void form.handleSubmit()
  }

  return {
    state: {},
    queries: {},
    mutations: {},
    functions: {
      handleSubmit,
    },
    features: {
      form,
    },
  }
}
