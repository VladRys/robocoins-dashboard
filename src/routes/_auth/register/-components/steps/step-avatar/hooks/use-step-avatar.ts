import { useForm } from '@tanstack/react-form'
import { useEffect, useState } from 'react'
import type { SyntheticEvent } from 'react'

import type { CarouselApi } from '#/components/ui'
import { AVATARS } from '#/routes/_auth/register/-constants'

import { RegisterStep } from '../../../../-schemas'
import { useRegisterContext } from '../../../register-provider'

export function useStepAvatar() {
  const register = useRegisterContext()

  const savedIndex = AVATARS.findIndex((key) => key === register.state.avatar)
  const initialIndex = savedIndex === -1 ? Math.floor(AVATARS.length / 2) : savedIndex

  const form = useForm({
    defaultValues: { avatar: AVATARS[initialIndex] },
    onSubmit: ({ value }) => {
      register.setState({ step: RegisterStep.View, avatar: value.avatar })
    },
  })

  const [api, setApi] = useState<CarouselApi>()

  useEffect(() => {
    if (!api) return

    const handleSelect = () => form.setFieldValue('avatar', AVATARS[api.selectedScrollSnap()])

    api.on('select', handleSelect)

    return () => {
      api.off('select', handleSelect)
    }
  }, [api, form])

  const handleSubmit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault()
    void form.handleSubmit()
  }

  return {
    state: {
      initialIndex,
    },
    queries: {},
    mutations: {},
    functions: {
      setApi,
      handleSubmit,
    },
    features: {
      form,
    },
  }
}
