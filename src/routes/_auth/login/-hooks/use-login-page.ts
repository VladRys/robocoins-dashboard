import { useForm } from '@tanstack/react-form'
import type { SyntheticEvent } from 'react'

import { LoginStateSchema } from '../-schemas'

export function useLoginPage() {
  const form = useForm({
    defaultValues: { password: '' },
    validators: { onChange: LoginStateSchema },
    onSubmit: () => {},
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
