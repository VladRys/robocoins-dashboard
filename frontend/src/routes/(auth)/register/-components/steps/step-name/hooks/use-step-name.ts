import { useForm } from "@tanstack/react-form";

import { RegisterStep, useRegisterContext } from "../../../register-provider";

export function useStepName() {
  const register = useRegisterContext();

  const form = useForm({
    defaultValues: { name: register.state.name ?? "" },
    onSubmit: ({ value }) => {
      register.goTo(RegisterStep.Group, { name: value.name.trim() });
    },
  });

  return {
    state: {},
    queries: {},
    mutations: {},
    functions: {},
    features: {
      form,
    },
  };
}
