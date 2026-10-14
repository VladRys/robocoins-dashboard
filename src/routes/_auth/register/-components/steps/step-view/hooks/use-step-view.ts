import { useNavigate } from '@tanstack/react-router'

import { useCreateStudentStudentRegisterPost } from '#/api/hooks'
import { LOCALSTORAGE_DID_REGISTER } from '#/routes/-constants'

import { LOCALSTORAGE_REGISTER_STATE } from '../../../../-constants'
import { CompleteRegisterStateSchema } from '../../../../-schemas'
import { useRegisterContext } from '../../../register-provider'

export function useStepView() {
  const register = useRegisterContext()

  const navigate = useNavigate()

  const registerMutation = useCreateStudentStudentRegisterPost({
    mutation: {
      onSuccess: () => {
        localStorage.removeItem(LOCALSTORAGE_REGISTER_STATE)
        localStorage.setItem(LOCALSTORAGE_DID_REGISTER, 'true')
        void navigate({ to: '/' })
      },
    },
  })

  const handleFinish = () => {
    const draft = CompleteRegisterStateSchema.safeParse(register.state)

    if (!draft.success) return

    const { name, avatar, courseName, groupId } = draft.data

    registerMutation.mutate({
      body: { name, avatar, course_name: courseName, group_id: groupId },
    })
  }

  return {
    state: {
      name: register.state.name,
      avatar: register.state.avatar,
      courseName: register.state.courseName,
      groupId: register.state.groupId,
    },
    mutations: {
      register: registerMutation,
    },
    functions: {
      handleFinish,
    },
    features: {},
  }
}
