import { useForm } from '@tanstack/react-form'
import { useEffect, useState } from 'react'
import type { SyntheticEvent } from 'react'

import type { CarouselApi } from '#/components/ui'

import { AVATAR_KEYS, Avatar } from '../../../../-constants'
import { RegisterStep, useRegisterContext } from '../../../register-provider'

export function useStepAvatar() {
  const register = useRegisterContext()

  const savedIndex = AVATAR_KEYS.findIndex((key) => key === register.state.avatar)
  const initialIndex = savedIndex === -1 ? Math.floor(AVATAR_KEYS.length / 2) : savedIndex

  const form = useForm({
    defaultValues: { avatar: AVATAR_KEYS[initialIndex] as Avatar },
    onSubmit: ({ value }) => {
      register.goTo(RegisterStep.View, { avatar: value.avatar })
    },
  })

  const [api, setApi] = useState<CarouselApi>()

  useEffect(() => {
    if (!api) return

    const handleSelect = () => form.setFieldValue('avatar', AVATAR_KEYS[api.selectedScrollSnap()])

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
