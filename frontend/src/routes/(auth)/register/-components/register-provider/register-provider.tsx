import { createContext, Dispatch, ReactNode, SetStateAction, use, useMemo, useState } from "react";

import { registerDraft } from "../../-lib";

export const RegisterStep = {
  Name: "name",
  Group: "group",
  Avatar: "avatar",
  View: "view",
} as const;
export type RegisterStep = (typeof RegisterStep)[keyof typeof RegisterStep];

export interface RegisterState {
  step: RegisterStep;
  name?: string;
  avatar?: string;
  groupId?: number;
  courseName?: string;
}

interface RegisterContextValue {
  goTo: (step: RegisterStep, updates?: Partial<Omit<RegisterState, "step">>) => void;
  update: (updates: Partial<RegisterState>) => void;
  state: RegisterState;
  setState: Dispatch<SetStateAction<RegisterState>>;
}

const RegisterContext = createContext<RegisterContextValue>({} as RegisterContextValue);

export interface RegisterProviderProps {
  initialState: RegisterState;
  children: ReactNode;
}

export function RegisterProvider({ initialState, children }: RegisterProviderProps) {
  const [state, setState] = useState<RegisterState>(initialState);

  const _setState: Dispatch<SetStateAction<RegisterState>> = (action) => {
    setState((current) => {
      const next = typeof action === "function" ? action(current) : action;
      registerDraft.save(next);
      return next;
    });
  };

  const update = (updates: Partial<RegisterState>) => {
    _setState((current) => ({ ...current, ...updates }));
  };

  const goTo = (step: RegisterStep, updates?: Partial<Omit<RegisterState, "step">>) => {
    _setState((current) => ({ ...current, ...updates, step }));
  };

  const contextValue = useMemo(() => ({ state, setState: _setState, update, goTo }), [state]);

  return <RegisterContext value={contextValue}>{children}</RegisterContext>;
}

export function useRegisterContext() {
  return use(RegisterContext);
}
