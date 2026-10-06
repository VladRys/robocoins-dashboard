import { useField } from "#/hooks";
import { useRegisterContext } from "../-components/register-provider/register-provider";

export function useRegisterPage() {
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
