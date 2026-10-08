import { createContext, ReactNode, use, useMemo, useState } from 'react'

import { Avatar } from '../../-constants'
import { registerState } from '../../-lib'

export const RegisterStep = {
  Name: 'name',
  Group: 'group',
  Avatar: 'avatar',
  View: 'view',
} as const
export type RegisterStep = (typeof RegisterStep)[keyof typeof RegisterStep]

export interface RegisterState {
  step: RegisterStep
  name?: string
  avatar?: Avatar
  groupId?: number
  courseName?: string
}

interface RegisterContextValue {
  goTo: (step: RegisterStep, updates?: Partial<Omit<RegisterState, 'step'>>) => void
  state: RegisterState
}

const RegisterContext = createContext<RegisterContextValue>({} as RegisterContextValue)

export interface RegisterProviderProps {
  initialState: RegisterState
  children: ReactNode
}

export function RegisterProvider({ initialState, children }: RegisterProviderProps) {
  const [state, setState] = useState<RegisterState>(initialState)

  const goTo = (step: RegisterStep, updates?: Partial<Omit<RegisterState, 'step'>>) => {
    const next = { ...state, ...updates, step }
    setState(next)
    registerState.save(next)
  }

  const contextValue = useMemo(() => ({ state, goTo }), [state])

  return <RegisterContext value={contextValue}>{children}</RegisterContext>
}

export function useRegisterContext() {
  return use(RegisterContext)
}
