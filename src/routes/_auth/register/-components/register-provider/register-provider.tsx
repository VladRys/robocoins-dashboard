import { createContext, ReactNode, use, useMemo, useState } from 'react'

import { LOCALSTORAGE_REGISTER_STATE } from '../../-constants'
import type { RegisterState } from '../../-schemas'

type NewState = Partial<Omit<RegisterState, 'step'>> & Pick<RegisterState, 'step'>

interface RegisterContextValue {
  setState: (newState: NewState) => void
  state: RegisterState
}

const RegisterContext = createContext<RegisterContextValue>({} as RegisterContextValue)

export interface RegisterProviderProps {
  initialState: RegisterState
  children: ReactNode
}

export function RegisterProvider({ initialState, children }: RegisterProviderProps) {
  const [state, setState] = useState<RegisterState>(initialState)

  const _setState = (newState: NewState) => {
    const next = { ...state, ...newState }
    setState(next)
    localStorage.setItem(LOCALSTORAGE_REGISTER_STATE, JSON.stringify(next))
  }

  const contextValue = useMemo(() => ({ state, setState: _setState }), [state])

  return <RegisterContext value={contextValue}>{children}</RegisterContext>
}

export function useRegisterContext() {
  return use(RegisterContext)
}
