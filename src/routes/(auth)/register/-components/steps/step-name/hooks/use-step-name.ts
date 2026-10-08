import { useForm } from '@tanstack/react-form'
import type { SyntheticEvent } from 'react'

import { RegisterStep, useRegisterContext } from '../../../register-provider'

const VALIDATORS = {
  name: {
    onSubmit: ({ value }: { value: string }) => value.trim() === '' || undefined,
  },
}

export function useStepName() {
  const register = useRegisterContext()

  const form = useForm({
    defaultValues: { name: register.state.name ?? '' },
    onSubmit: ({ value }) => {
      register.goTo(RegisterStep.Group, { name: value.name.trim() })
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
      fields: {
        name: {
          validators: VALIDATORS.name,
        },
      },
    },
  }
}
