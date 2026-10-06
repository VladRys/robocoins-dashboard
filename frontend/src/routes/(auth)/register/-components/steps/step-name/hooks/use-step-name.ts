import { useField } from "#/hooks";

import { useRegisterContext } from "../../../register-provider/register-provider";

export function useStepName() {
  const context = useRegisterContext();

  const nameField = useField("");

  const handleRegister = () => {
    if (nameField.getValue().trim() === "") return;
  };

  return {
    state: {},
    queries: {},
    mutations: {},
    functions: {
      handleRegister,
    },
    features: {
      nameField,
    },
  };
}
