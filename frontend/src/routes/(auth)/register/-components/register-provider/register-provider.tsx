import { createContext, ReactNode, use, useMemo, useState } from "react";

export type RegisterStep = "name";

interface RegisterContextValue {
  step: RegisterStep;
  setStep: (step: RegisterStep) => void;
}

const RegisterContext = createContext<RegisterContextValue>(
  {} as RegisterContextValue,
);

export interface RegisterProviderProps {
  children: ReactNode;
}

export function RegisterProvider({ children }: RegisterProviderProps) {
  const [step, setStep] = useState<RegisterStep>("name");

  const contextValue = useMemo(() => ({ step, setStep }), [step]);

  return <RegisterContext value={contextValue}>{children}</RegisterContext>;
}

export function useRegisterContext() {
  return use(RegisterContext);
}
